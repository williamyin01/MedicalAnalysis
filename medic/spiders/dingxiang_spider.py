import scrapy
import re
from medic.items import QAItem
from scrapy.loader import ItemLoader
import sqlite3
import logging

class dxSpider(scrapy.Spider):
    name = 'dxspider'
    allow_domains = ['dxy.com']
    custom_settings = {
        "USER_AGENT": 'Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
        # auto throttle
        # 'AUTOTHROTTLE_ENABLED': True,
        # 'AUTOTHROTTLE_TARGET_CONCURRENCY': 1,
        'ITEM_PIPELINES': {
            'medic.pipelines.DxAdvPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 190,
        },
        'RETRY_TIMES': 3,
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'SQLITE_FILE': 'dxadv.db',
        'SQLITE_TABLE': 'dialogs',
    }

    q_id = 0
    def start_requests(self):
        q_id_list = self.get_q_ids()
        # q_id_list = q_id_list[0:1]
        base_url = 'https://m.dxy.com/q'
        for id in q_id_list:
            self.q_id = id
            next_href = base_url + '/' + str(id)
            yield scrapy.Request(next_href, self.parse)
        
    def parse(self, response):
        n_q_a = 3
        # if response.status == 200:
        # it = ItemLoader(item=MedicItem())
        # self.count += 1
        it = QAItem()
        date = response.xpath('//p[@class="dialog-child-person-right-date"]/text()').get()
        doctor_id = response.xpath('//a[@class="question-detail-doctor"]/@href').get()
        doctor_id = int(re.search(r'/user/(\d+)', doctor_id).group(1))
        questions = response.xpath('//article[@class="dialog-content divide"]/div//p[@class="dialog-child-content-text patient-color"]')
        questions = [q.xpath('string(.)').get() for q in questions]

        answers = []
        for i in range(len(questions)):
            i+=1
            curr_answers = response.xpath('//article[@class="dialog-content divide"]/*/following-sibling::section[count(preceding-sibling::div)={0}]//p[@class="dialog-child-content-text patient-color"]'.format(i))
            answers.append([a.xpath('string(.)').get() for a in curr_answers])
        answers = [''.join(a_list) for a_list in answers]

        questions = self.keep_list_length(questions, n_q_a)
        answers = self.keep_list_length(answers, n_q_a)
        it['date'] = date
        it['doctor_id'] = doctor_id
        it['question'] =  questions[0]
        it['answer'] = answers[0]
        it['q1'] =  questions[1]
        it['a1'] =  answers[1]
        it['q2'] =  questions[2]
        it['a2'] =  answers[2]
        it['id'] = self.q_id
        yield it
    def keep_list_length(self, target_list, target_length, filler=''):
        return target_list[:target_length] + [filler]*(target_length - len(target_list))
    def get_q_ids(self):
        conn = sqlite3.connect('dxadv.db')
        cursor = conn.cursor()
        cursor.execute('select id from dialogs where question is null or answer is null')
        q_ids = cursor.fetchall()
        q_ids = [x[0] for x in q_ids]
        cursor.close()
        return q_ids