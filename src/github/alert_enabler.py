import logging
import time

import requests


class AlertEnabler(object):
    def __init__(self, token):
        self.repo_url_fmt = 'https://api.github.com/orgs/{}/repos?page={}&per_page=100'
        self.token = token

    def run(self, org_name, start_page):
        if start_page != 0:
            logging.info("Starting at page {}".format(start_page))
        idx = 0
        page = start_page
        while True:
            logging.info("Getting repo IDs for org {}. Page {}".format(org_name, page))
            repo_url = self.repo_url_fmt.format(org_name, page)
            repo_ids = [r.get('id') for r in self.get_endpoint(repo_url)
                        if not r.get('archived', True) and not r.get('disabled', True)]
            if len(repo_ids) == 0:
                break
            logging.info("Retrieved {} repo IDs for {}".format(len(repo_ids), org_name))
            for repo_id in repo_ids:
                resp = self.enable_for_repo(repo_id)
                success = resp.status_code == 204
                if not success:
                    logging.warn("Unable to enable vulnerabilities for repo {}. Status code: {}. Body: {}"
                                 .format(repo_id, resp.status_code, resp.text))
                if idx % 10 == 0:
                    logging.info('Sent enable for {} repos so far...'.format(idx))
                time.sleep(0.5)
                idx += 1

            page += 1
        logging.info('Done! Flagged {} repos for security alerts.'.format(idx))

    def get_endpoint(self, url):
        resp = requests.get(url=url, headers={'Authorization': 'Bearer {}'.format(self.token),
                                              'Accept': 'application/vnd.github.dorian-preview+json'})
        return resp.json()

    def enable_for_repo(self, repo_id):
        enable_url = 'https://api.github.com/repositories/{}/vulnerability-alerts'.format(repo_id)
        resp = requests.put(url=enable_url, headers={'Authorization': 'Bearer {}'.format(self.token),
                                                     'Accept': 'application/vnd.github.dorian-preview+json'})

        return resp
