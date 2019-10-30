import json

from src.config import Config
from src.github.graphql_call import RepoVulnerabilityCall

if __name__ == '__main__':
    conf = Config()
    query = RepoVulnerabilityCall()
    out = query.pages(conf.github.access_token, org_name=conf.github.org_name)
    filtered = [x for x in out if len(x.get('node').get('vulnerabilityAlerts').get('edges')) > 0]
    print(json.dumps(filtered, indent=2))

    for item in filtered:
        data = item.get('node')
        url = data.get('url')
        print('URL: {}'.format(url))
        for vuln in data.get('vulnerabilityAlerts').get('edges'):
            vuln_data = vuln.get('node').get('securityVulnerability')
            ecosystem = vuln_data.get('package').get('ecosystem')
            package = vuln_data.get('package').get('name')
            version_range = vuln_data.get('vulnerableVersionRange')
            severity = vuln_data.get('severity')
            print('{} dependency {} versions {} - {}'.format(ecosystem, package, version_range, severity))