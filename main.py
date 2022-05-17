import os
import requests
import argparse
import numpy as np
from collections import OrderedDict
from subprocess import call
from concurrent.futures import ThreadPoolExecutor

def get_fake_headers ():

    ''' List of fake user-agent headers for scraping
    Tutorial: https://www.scrapehero.com/how-to-fake-and-rotate-user-agents-using-python-3
    List user-agents: https://developers.whatismybrowser.com/useragents/explore/operating_system_name/windows/
    '''

    headers_list = [

        # Firefox 77 Mac
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        },

        # Firefox 77 Windows
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        },

        # Chrome 83 Mac
        {
            "Connection": "keep-alive",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
            "Referer": "https://www.google.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
        },

        # Chrome 83 Windows
        {
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Referer": "https://www.google.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9"
        }
    ]

    # Create ORDERED dict from Headers above
    ordered_headers_list = []
    for headers in headers_list:
        h = OrderedDict()
        for header, value in headers.items():
            h[header] = value
        ordered_headers_list.append(h)


    return ordered_headers_list



class DockerRegistryCrawler():

    def __init__(self, registry: str, worker: str) -> None:
        self.registry = registry
        self.worker = worker
        self.size = os.cpu_count()
        self.cursor = None
        self.headers_list = get_fake_headers()


    def run(self):

        # Create a thread pool to limit number of worker calls
        with ThreadPoolExecutor(max_workers=self.size) as pool:
            for repository in self.list_repos():
                for tag in self.get_tags(repository):
                    pool.submit(self._run_worker, repository, tag)

    # List all repositories in the registry
    def list_repos(self) -> list[str]:
        return requests.get(self.registry + "/v2/_catalog", headers=np.random.choice(self.headers_list),verify=False).json()["repositories"]

    # Find all tags in the repository
    def get_tags(self, repository):
        return requests.get(self.registry + "/v2/" + repository + "/tags/list", headers=np.random.choice(self.headers_list),verify=False).json()['tags']

    def _run_worker(self, repository, tag):
        call(['python', self.worker, repository, tag])


parser = argparse.ArgumentParser()

parser.add_argument('registry', type=str, help='Specify registry to scan')
parser.add_argument('worker', type=str, help='Specify the worker script that will examine the images')


args = parser.parse_args()

if __name__ == '__main__':
    crawler = DockerRegistryCrawler(args.registry, args.worker)
    crawler.run()
