import scrapy
import re
from medic.items import MedicItem
from scrapy.loader import ItemLoader
class dxSpider(scrapy.Spider):
    name = 'dxspider'
    allow_domains = ['dxy.com']
    custom_settings = {
        "USER_AGENT": 'Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
        # "FEED_URI": 'result-dx.csv',
        # "FEED_FORMAT": 'CSV',
        'HTTPERROR_ALLOWED_CODES': [302,403, 404],
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'SQLITE_FILE': 'dx.db',
        'SQLITE_TABLE': 'dxdata',
    }

    q_id = 10000
    def start_requests(self):
        START_ID = 10000
        END_ID = 20000
        base_url = 'https://m.dxy.com/q'
        for id in range(START_ID, END_ID):
            self.q_id = id
            next_href = base_url + '/' + str(id)
            yield scrapy.Request(next_href, self.parse)
        
    def parse(self, response):
        n_q_a = 3
        if response.status == 200:
            # it = ItemLoader(item=MedicItem())
            # self.count += 1
            it = MedicItem()
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
            it['q_id'] = self.q_id
            # aaa = it.load_item()
            # yield it.load_item()
            yield it
    def keep_list_length(self, target_list, target_length, filler=''):
        return target_list[:target_length] + [filler]*(target_length - len(target_list))