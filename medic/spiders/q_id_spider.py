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
        # 'USER_AGENT': 'Mozilla/5.num (Windows NT 10.num; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.num.3729.108 Safari/537.36',
        # 'DOWNLOAD_DELAY': 0.5,
        'JOBDIR': 'crawls/q_id_spider-1',
        'SQLITE_FILE': 'dxadv.db',
        'SQLITE_TABLE': 'dialogs',
        'ITEM_PIPELINES': {
            'medic.pipelines.DxAdvPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            # 'medic.middlewares.CheckURLMiddleware': 100,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 190,
            'medic.scrapy_proxies.ProxyMiddleware': 200,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 210,
            'random_useragent.RandomUserAgentMiddleware': 150,
            'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
        },
        # user agents list
        'USER_AGENT_LIST': "medic/useragents.txt",
        # random proxy settings
        # 'PROXY_LIST': 'proxies.txt',
        # 'CUSTOM_PROXY': get_proxy(),
        # 'PROXY_MODE': 2,
        'RETRY_TIMES': 3,
        # 'PROXY_API': 'http://127.0.0.1:5010',
        'PROXY_API': 'http://api.ip.data5u.com/dynamic/get.html?order=bba7c6b714bf8fceb03108a33960b4b6&sep=3'
    }

    def start_requests(self):
        items_per_page = 10
        doctor_ids = self.get_doctor_id_list()
        # doctor_ids = [28235]
        for id in doctor_ids:
            for page_index in range(1, 25):
                query_param = {
                    'items_per_page': items_per_page,
                    'doctor_user_id': id,
                }
                if page_index > 1:
                    query_param.update({
                    'page_index': page_index,
                    'append': True,
                    })
                url = 'https://ask.dxy.com/view/i/question/list/answered/public?' + urlencode(query_param)
                yield scrapy.Request(url, meta={'doctor_id': id, 'nitems': items_per_page}, callback=self.parse)
    # get list of q id and call for further scraping
    def parse(self, response):
        jsonresponse = json.loads(response.body)
        qa_list = []
        for i in range(0, response.meta['nitems']):
            try:
                q_id = jsonresponse['data']['items'][i]['id']
            except IndexError:
                break
            qa_list.append(q_id)

        # store qa_list
        for q_id in qa_list:
            it = QAItem()
            it['id'] = q_id
            it['doctor_id'] = response.meta['doctor_id']
            yield it
    #     param = {
    #         'id': response.meta['doctor_id'],
    #         'type_list': '0,1,2',
    #         'refer':'',
    #     }
    #     url = 'https://ask.dxy.com/view/i/biz/question?' + urlencode(param)
    #     yield scrapy.Request(url, meta={'qa_list':qa_list,  'doctor_id': response.meta['doctor_id']}, callback=parse_qa)
    

    # def parse_qa(self, response):
    #     jsresp = json.loads(response.body)
    #     jsresp = jsresp['data']['items'][0]
    #     qa_il = ItemLoader(item=QAItem, response=response)
    #     qa_il.add_value('id', )
    #     qa_il.add_value('date', jsresp['question']['create_time'])
    #     qa_il.add_value('doctor_id', response.meta['doctor_id'])

    # get all doctors' id from database
    def get_doctor_id_list(self):
        conn = sqlite3.connect('dxadv.db')
        cursor = conn.cursor()
        cursor.execute('select id from doctors')
        doctor_ids = cursor.fetchall()
        doctor_ids = [x[0] for x in doctor_ids]
        cursor.close()
        return doctor_ids

            