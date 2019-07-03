import re
import random
import base64
import logging
import requests
import json
from time import sleep
from scrapy.exceptions import NotSupported, IgnoreRequest

log = logging.getLogger('scrapy.proxies')
logging.getLogger("requests").setLevel(logging.WARNING)

class ProxyMiddleware(object):
    # choose a proxy from api, and check if it's available for extracting json
    # if not available, delete it from proxy pool and find a new one
    def __init__(self, settings):
        self.proxy_api = settings.get('PROXY_API')
        self.chosen_proxy = self.get_proxy()
        if not self.chosen_proxy:
            raise ValueError('No proxy available during initialization')
    def get_proxy(self):
        proxy = ''
        while True:
            proxy = requests.get(self.proxy_api + '/get').content.decode()
            # proxy = requests.get(self.proxy_api).content.decode()
            # if 'too many' in proxy:
            if 'no proxy' in proxy:
                log.debug('No proxy available, retry after 1 second')
                # sleep(1)
            else:
                log.debug('get new proxy ip: {}'.format(proxy))
                break
        return 'http://' + proxy.strip()
    def delete_proxy(self, proxy):
        parts = re.match('(\w+://)([^:]+?:[^@]+?@)?(.+)', proxy.strip())
        if not parts:
            raise ValueError('Deleting failed: {}'.format(proxy))
        requests.get(self.proxy_api + '/delete/?proxy={}'.format(parts.group(3)))
        # return None
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)
    
    def process_request(self, request, spider):
        # request.meta['proxy'] = self.get_proxy().strip()
        request.meta['proxy'] = self.chosen_proxy
        log.debug('Using proxy <{0}> to visit {1}'.format(self.chosen_proxy, request.meta['query_param']))
    def process_response(self, request, response, spider):
        jsresponse = json.loads(response.body)
        if 'error' in jsresponse:
            proxy = request.meta['proxy']
            self.delete_proxy(proxy)
            if proxy == self.chosen_proxy:
                self.chosen_proxy = self.get_proxy()
            else:
                request.meta['proxy'] = self.chosen_proxy
            log.debug('Proxy ip <{0}> is banned in json from {1}'.format(proxy, request.meta['query_param']))
            return request
        if not jsresponse['data']['items']:
            raise IgnoreRequest
        return response
    def process_exception(self, request, exception, spider):
        if 'proxy' not in request.meta:
            return None
        proxy = request.meta['proxy']
        self.delete_proxy(proxy)
        if proxy == self.chosen_proxy:
            self.chosen_proxy = self.get_proxy()
        else:
            request.meta['proxy'] = self.chosen_proxy
        log.debug('Proxy ip {1} is banned from {0}'.format(request.meta['query_param'], proxy))
        return request
