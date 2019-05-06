import scrapy
import json
from medic.items import QAItem
from urllib.parse import urlencode
from medic.items import QAItem
import sqlite3

# spider for quesiton id
class QIDSpider(scrapy.Spider):
    name = 'q_id_spider'
    allow_domains = ['dxy.com']
    custom_settings = {
        # 'DOWNLOAD_DELAY': 0.5,
        'JOBDIR': 'crawls/q_id_spider-1',
        'SQLITE_FILE': 'dxadv.db',
        'SQLITE_TABLE': 'dialogs',

        'ITEM_PIPELINES': {
            'medic.pipelines.DxAdvPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 190,
            'medic.scrapy_proxies.ProxyMiddleware': 200,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 210,
            'random_useragent.RandomUserAgentMiddleware': 150,
            'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
        },
        # user agents list
        'USER_AGENT_LIST': "medic/useragents.txt",
        'RETRY_TIMES': 3,
        'PROXY_API': 'http://127.0.0.1:5010',
    }

    def start_requests(self):
        items_per_page = 10
        doctor_ids = self.get_doctor_id_list()
        # doctor_ids = [28235]
        for id in doctor_ids:
            query_param = {
                'items_per_page': items_per_page,
                'doctor_user_id': id,
            }
            url = 'https://ask.dxy.com/view/i/question/list/answered/public?' + urlencode(query_param)
            yield scrapy.Request(url, meta={'query_param': query_param}, callback=self.parse_first)
    # retrieve total_pages from first json and call for furthing scraping
    def parse_first(self, response):
        jsonresponse = json.loads(response.body)
        total_pages = jsonresponse['data']['total_pages']
        for i in range(2, total_pages+1):
            query_param = response.meta['query_param']
            query_param.update({
                'page_index': i,
                'append': True,
            })
            url = 'https://ask.dxy.com/view/i/question/list/answered/public?' + urlencode(query_param)
            yield scrapy.Request(url, meta={'query_param': query_param}, callback=self.parse)
        
    # get list of q id and call for further scraping
    def parse(self, response):
        jsonresponse = json.loads(response.body)
        for i in range(0, response.meta['query_param']['items_per_page']):
            try:
                q_id = jsonresponse['data']['items'][i]['id']
            except IndexError:
                break
            # store qa_list
            it = QAItem()
            it['id'] = q_id
            it['doctor_id'] = response.meta['query_param']['doctor_user_id']
            yield it

    # get all doctors' id from database
    def get_doctor_id_list(self):
        conn = sqlite3.connect('dxadv.db')
        cursor = conn.cursor()
        cursor.execute('select id from doctors')
        doctor_ids = cursor.fetchall()
        doctor_ids = [x[0] for x in doctor_ids]
        cursor.close()
        return doctor_ids

            