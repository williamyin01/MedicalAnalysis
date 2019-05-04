# Copyright (C) 2013 by Aivars Kalvans <aivars.kalvans@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

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

class Mode:
    RANDOMIZE_PROXY_EVERY_REQUESTS, RANDOMIZE_PROXY_ONCE, SET_CUSTOM_PROXY, GET_RANDOM_PROXY = range(4)


class RandomProxy(object):
    def get_proxy(self):
        ip = requests.get('http://127.0.0.1:5010/get').content.decode()
        return 'http://' + ip
    def delete_proxy(self, proxy):
        requests.get('http://127.0.0.1:5010/delete/?proxy={}'.format(proxy))

    def __init__(self, settings):
        self.mode = settings.get('PROXY_MODE')
        self.proxy_list = settings.get('PROXY_LIST')
        self.chosen_proxy = ''

        if self.mode == Mode.RANDOMIZE_PROXY_EVERY_REQUESTS or self.mode == Mode.RANDOMIZE_PROXY_ONCE:
            if self.proxy_list is None:
                raise KeyError('PROXY_LIST setting is missing')
            self.proxies = {}
            fin = open(self.proxy_list)
            try:
                for line in fin.readlines():
                    parts = re.match('(\w+://)([^:]+?:[^@]+?@)?(.+)', line.strip())
                    if not parts:
                        continue

                    # Cut trailing @
                    if parts.group(2):
                        user_pass = parts.group(2)[:-1]
                    else:
                        user_pass = ''

                    self.proxies[parts.group(1) + parts.group(3)] = user_pass
            finally:
                fin.close()
            if self.mode == Mode.RANDOMIZE_PROXY_ONCE:
                self.chosen_proxy = random.choice(list(self.proxies.keys()))
        elif self.mode == Mode.SET_CUSTOM_PROXY:
            # custom_proxy = settings.get('CUSTOM_PROXY')
            custom_proxy = self.get_proxy()
            self.proxies = {}
            parts = re.match('(\w+://)([^:]+?:[^@]+?@)?(.+)', custom_proxy.strip())
            if not parts:
                raise ValueError('CUSTOM_PROXY is not well formatted')

            if parts.group(2):
                user_pass = parts.group(2)[:-1]
            else:
                user_pass = ''

            self.proxies[parts.group(1) + parts.group(3)] = user_pass
            self.chosen_proxy = parts.group(1) + parts.group(3)
            

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        # Don't overwrite with a random one (server-side state for IP)
        if 'proxy' in request.meta:
            if request.meta["exception"] is False:
                return
        request.meta["exception"] = False
        if len(self.proxies) == 0:
            raise ValueError('All proxies are unusable, cannot proceed')

        if self.mode == Mode.RANDOMIZE_PROXY_EVERY_REQUESTS:
            proxy_address = random.choice(list(self.proxies.keys()))
        else:
            proxy_address = self.chosen_proxy

        proxy_user_pass = self.proxies[proxy_address]

        if proxy_user_pass:
            request.meta['proxy'] = proxy_address
            basic_auth = 'Basic ' + base64.b64encode(proxy_user_pass.encode()).decode()
            request.headers['Proxy-Authorization'] = basic_auth
        else:
            log.debug('Proxy user pass not found')
        log.debug('Using proxy <%s>, %d proxies left' % (
                proxy_address, len(self.proxies)))

    def process_exception(self, request, exception, spider):
        if 'proxy' not in request.meta:
            return
        if self.mode == Mode.RANDOMIZE_PROXY_EVERY_REQUESTS or self.mode == Mode.RANDOMIZE_PROXY_ONCE:
            proxy = request.meta['proxy']
            try:
                del self.proxies[proxy]
            except KeyError:
                pass
            request.meta["exception"] = True
            if self.mode == Mode.RANDOMIZE_PROXY_ONCE:
                self.chosen_proxy = random.choice(list(self.proxies.keys()))
            log.info('Removing failed proxy <%s>, %d proxies left' % (
                proxy, len(self.proxies)))
    def process_response(self, request, response, spider):
        if 'error' in json.loads(response.body):
            self.delete_proxy(self.chosen_proxy)
            self.chosen_proxy = self.get_proxy()
            self.proxies[self.chosen_proxy]=''
            log.debug('Proxy ip {} is banned. Drop it.'.format(request.meta['proxy']))
            return request
        return response

class ProxyMiddleware(object):
    # proxy middlewares developed by me
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
            # proxy = requests.get(self.proxy_api + '/get').content.decode()
            proxy = requests.get(self.proxy_api).content.decode()
            # if 'no proxy' in proxy:
            if not proxy[0].isdigit():
                log.debug('No proxy available, retry after 1 second')
                sleep(1)
            else:
                break
        return 'http://' + proxy.strip()
    def delete_proxy(self, proxy):
        # parts = re.match('(\w+://)([^:]+?:[^@]+?@)?(.+)', proxy.strip())
        # if not parts:
        #     raise ValueError('Deleting failed: {}'.format(proxy))
        # requests.get(self.proxy_api + '/delete/?proxy={}'.format(parts.group(3)))
        return None
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)
    
    def process_request(self, request, spider):
        # request.meta['proxy'] = self.get_proxy().strip()
        request.meta['proxy'] = self.chosen_proxy
        log.debug('Using proxy <{0}>'.format(self.chosen_proxy))
    def process_response(self, request, response, spider):
        jsresponse = json.loads(response.body)
        if 'error' in jsresponse:
            proxy = request.meta['proxy']
            self.delete_proxy(proxy)
            self.chosen_proxy = self.get_proxy()
            log.debug('Proxy ip <{0}> is banned in json from {1}'.format(proxy, request.url))
            return request
        if not jsresponse['data']['items']:
            raise IgnoreRequest
        return response
    def process_exception(self, request, exception, spider):
        if 'proxy' not in request.meta:
            return None
        proxy = request.meta['proxy']
        self.delete_proxy(proxy)
        self.chosen_proxy = self.get_proxy()
        log.debug('Cannot connect to the site. Dropping proxy <{}>.'.format(request.meta['proxy']))
        return request



