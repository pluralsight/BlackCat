import logging
import time

from blackcat.github.alert_enabler import AlertEnabler
from blackcat.github.graphql_call import RepoVulnerabilityCall
from blackcat.postprocessing.post_processor import BlackCatPostProcessor
from blackcat.postprocessing.steps.trim_to_relevant_data import PostStepFlattenRelevantData
from blackcat.util.splunk_hec_handler import SplunkHecHandler


class BlackCat(object):
    @classmethod
    def _log_license(cls, logger, url, start_time, data):
        license_info = data.get('licenseInfo')

        if license_info:
            license_info['run_id'] = start_time
            license_info['repo_url'] = url
            if not logger:
                logging.info(license_info)
            else:
                # Set a custom source type for splunk
                if len(logger.handlers) > 0 and isinstance(logger.handlers[0], SplunkHecHandler):
                    # TODO: Should this be configurable?
                    license_info['fields'] = {'sourcetype': logger.handlers[0].sourcetype + '_license'}

                spdx_id = license_info.get('spdxId')
                if spdx_id and not license_info.get('pseudoLicense'):
                    # If this license is known, replace the body with a link for output.
                    license_info['body'] = 'See https://spdx.org/licenses/{}#licenseText'.format(spdx_id)
                logger.info(license_info)

    @classmethod
    def scan_org(cls, conf, org_name, start_time):
        query = RepoVulnerabilityCall()
        out = query.pages(conf.github.access_token, org_name=org_name)
        filtered = [x for x in out if len(x.get('node').get('vulnerabilityAlerts').get('edges')) > 0
                    or x.get('node').get('licenseInfo')]

        for item in filtered:
            data = item.get('node')
            url = data.get('url')
            logging.debug('URL: {}'.format(url))
            # Log license data if present
            cls._log_license(conf.logging.logger, url, start_time, data)

            for vuln in data.get('vulnerabilityAlerts').get('edges'):
                vuln_data = BlackCatPostProcessor.run(start_time, org_name, url, vuln)

                # If an external logger such as splunk or syslog has been set, log the vuln there.
                # Otherwise, log to standard logger.
                if conf.logging.logger:
                    conf.logging.logger.info(vuln_data)
                else:
                    logging.info(vuln_data)

                ecosystem = vuln_data.get('package').get('ecosystem')
                package = vuln_data.get('package').get('name')
                version_range = vuln_data.get('vulnerableVersionRange')
                severity = vuln_data.get('severity')
                logging.info('{} dependency {} versions {} - {}'.format(ecosystem, package, version_range, severity))

    @classmethod
    def execute_cli(cls, args, conf):
        enabler = None
        if args and args.enable:
            enabler = AlertEnabler(conf.github.access_token)

        BlackCatPostProcessor.add_post_step(PostStepFlattenRelevantData())

        # Get time since epoch
        start_time = round(time.time())

        # Query vulnerabilities
        for org_name in conf.github.org_names:
            if args and args.enable:
                logging.info('Enabling alerts for Organization {}'.format(org_name))
                enabler.run(org_name, args.enable_start_page)
            else:
                cls.scan_org(conf, org_name, start_time)

        total_time = round(time.time()) - start_time
        logging.info('Finished in %d seconds.', total_time)
