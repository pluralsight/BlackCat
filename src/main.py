import json
import logging
import os

from src.config import Config
from src.github.graphql_call import RepoVulnerabilityCall
from src.run_id import RunId

logging.basicConfig(format='%(asctime)s %(message)s')
logging.getLogger().setLevel(logging.DEBUG)

if __name__ == '__main__':
    # Track the current run ID
    run_id = RunId()

    conf = Config()

    # If config and logging worked, we inc run id, even if the API calls or filtering fail.
    run_id.inc_run_id()

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
            vuln_data['run_id'] = run_id.value
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