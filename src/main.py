#!/usr/bin/env python3
import argparse
import json
import logging
import time

from github.alert_enabler import AlertEnabler
from github.graphql_call import RepoVulnerabilityCall
from util.config import Config
from util.splunk_hec_handler import SplunkHecHandler

logging.basicConfig(format='%(asctime)s %(message)s')
logging.getLogger().setLevel(logging.DEBUG)


def log_license(logger, url, start_time, data):
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


def log_item(conf, start_time, item):
    data = item.get('node')
    url = data.get('url')
    logging.info('URL: {}'.format(url))

    # License data
    log_license(conf.logging.logger, url, start_time, data)
    # Vuln data
    for vuln in data.get('vulnerabilityAlerts').get('edges'):
        node_dict = vuln.get('node')
        # Start with the base vulnerability object
        out_dict = node_dict.get('securityVulnerability')
        # Get metadata fields
        dismisser = node_dict.get('dismisser')
        dismissed_at = node_dict.get('dismissedAt')
        dismissed_reason = node_dict.get('dismissReason')
        manifest_file = node_dict.get('vulnerableManifestPath')

        # Push metadata into vuln object
        out_dict['dismisser'] = dismisser
        out_dict['dismissed_at'] = dismissed_at
        out_dict['dismissed_reason'] = dismissed_reason
        out_dict['manifest_file'] = manifest_file

        # Push our metadata, repo url and run id
        out_dict['run_id'] = start_time
        out_dict['repo_url'] = url

        # If an external logger such as splunk or syslog has been set, log the vuln there.
        # Otherwise, log to standard logger.
        # if conf.logging.logger:
        #     conf.logging.logger.info(out_dict)
        # else:
        #     logging.info(out_dict)

        ecosystem = out_dict.get('package').get('ecosystem')
        package = out_dict.get('package').get('name')
        version_range = out_dict.get('vulnerableVersionRange')
        severity = out_dict.get('severity')
        logging.info('{} dependency {} versions {} - {}'.format(ecosystem, package, version_range, severity))


def handle_org(conf, org_name, start_time):
    query = RepoVulnerabilityCall()
    out = query.pages(conf.github.access_token, org_name=org_name)
    filtered = [x for x in out if len(x.get('node').get('vulnerabilityAlerts').get('edges')) > 0
                or x.get('node').get('licenseInfo')]
    logging.debug(json.dumps(filtered, indent=2))

    for item in filtered:
        log_item(conf, start_time, item)


def run(args, conf):
    enabler = None
    if args.enable:
        enabler = AlertEnabler(conf.github.access_token)

    # Get time since epoch
    start_time = round(time.time())

    # Query vulnerabilities
    for org_name in conf.github.org_names:
        if args.enable:
            logging.info('Enabling alerts for Organization {}'.format(org_name))
            enabler.run(org_name, args.enable_start_page)
        else:
            handle_org(conf, org_name, start_time)

    total_time = round(time.time()) - start_time
    logging.info('Finished in %d seconds.', total_time)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Manage or enable security alerts for github.')
    parser.add_argument('--enable', action='store_true',
                        help='Don\'t run a scan. Instead, enable alerts for all repos.')
    parser.add_argument('--enable-start-page', type=int, default=0, help='Set the start page for an enable run. '
                                                                         'Has no effect if --enable isn\'t set.')
    run(parser.parse_args(), Config())
