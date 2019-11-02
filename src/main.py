#!/usr/bin/env python3

import json
import logging
import time

from github.graphql_call import RepoVulnerabilityCall
from util.config import Config

logging.basicConfig(format='%(asctime)s %(message)s')
logging.getLogger().setLevel(logging.DEBUG)

if __name__ == '__main__':
    conf = Config()
    # Get time since epoch
    start_time = round(time.time())

    # Query vulnerabilities
    query = RepoVulnerabilityCall()
    out = query.pages(conf.github.access_token, org_name=conf.github.org_name)
    filtered = [x for x in out if len(x.get('node').get('vulnerabilityAlerts').get('edges')) > 0]
    print(json.dumps(filtered, indent=2))

    for item in filtered:
        data = item.get('node')
        url = data.get('url')
        logging.info('URL: {}'.format(url))
        for vuln in data.get('vulnerabilityAlerts').get('edges'):
            vuln_data = vuln.get('node').get('securityVulnerability')
            vuln_data['run_id'] = start_time
            vuln_data['repo_url'] = url
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

    total_time = round(time.time()) - start_time
    logging.info('Finished in %d seconds.', total_time)