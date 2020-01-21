import logging
import time

from github.alert_enabler import AlertEnabler
from github.graphql_call import RepoVulnerabilityCall
from postprocessing.post_processor import BlackCatPostProcessor
from postprocessing.steps.trim_to_relevant_data import PostStepFlattenRelevantData


class BlackCat(object):
    @staticmethod
    def scan_org(conf, org_name, start_time):
        query = RepoVulnerabilityCall()
        out = query.pages(conf.github.access_token, org_name=org_name)
        filtered = [x for x in out if len(x.get('node').get('vulnerabilityAlerts').get('edges')) > 0]

        for item in filtered:
            data = item.get('node')
            url = data.get('url')
            logging.debug('URL: {}'.format(url))
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
        if args.enable:
            enabler = AlertEnabler(conf.github.access_token)

        BlackCatPostProcessor.add_post_step(PostStepFlattenRelevantData())

        # Get time since epoch
        start_time = round(time.time())

        # Query vulnerabilities
        for org_name in conf.github.org_names:
            if args.enable:
                logging.info('Enabling alerts for Organization {}'.format(org_name))
                enabler.run(org_name, args.enable_start_page)
            else:
                cls.scan_org(conf, org_name, start_time)

        total_time = round(time.time()) - start_time
        logging.info('Finished in %d seconds.', total_time)
