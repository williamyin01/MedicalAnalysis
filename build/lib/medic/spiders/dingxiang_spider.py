import scrapy
import re
from medic.items import MedicItem
from scrapy.loader import ItemLoader
class dxSpider(scrapy.Spider):
    name = 'dxspider'
    allow_domains = ['dxy.com']
    start_urls = ['https://m.dxy.com/q/10000']
    custom_settings = {
        "USER_AGENT": 'Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
        # "FEED_URI": 'result-dx.csv',
        # "FEED_FORMAT": 'CSV',
        'HTTPERROR_ALLOWED_CODES': [302,403, 404],
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'SQLITE_FILE': 'dx.db',
        'SQLITE_TABLE': 'dxdata',
    }


    count = 0
    q_id = 10000
    END_ID = 100000
    def start_requests(self):
        base_url = 'https://m.dxy.com/q'
        while self.q_id < self.END_ID:
            self.q_id += 1
            next_href = base_url + '/' + str(self.q_id)
            yield scrapy.Request(next_href, self.parse)
        
    def parse(self, response):
        n_q_a = 8
        if response.status == 200:
            # it = ItemLoader(item=MedicItem())
            self.count += 1
            it = MedicItem()
            date = response.xpath('//p[@class="dialog-child-person-right-date"]/text()').get()
            doctor_id = response.xpath('//a[@class="question-detail-doctor"]/@href').get()
            doctor_id = int(re.search(r'/user/(\d+)', doctor_id).group(1))
            # q_a = response.xpath('//p[@class="dialog-child-content-text patient-color"]')
            questions = response.xpath('//div[@class="question-detail"]/article/div//p[@class="dialog-child-content-text patient-color"]')
            questions = [q.xpath('string(.)').get() for q in questions]
            # answers = []
            # for i in len(questions):
            #     i+=1
            #     curr_answers = response.xpath('//div[@class="question-detail"]/article/div[{0}]/following-sibling::section[count(preceding-sibling::div)={0}]//p[@class="dialog-child-content-text patient-color"]'.format(i))
            #     answers.append([a.xpath('string(.)').get() for a in curr_answers])
            answers = response.xpath('//div[@class="question-detail"]/article/section//p[@class="dialog-child-content-text patient-color"]')
            answers = [a.xpath('string(.)').get() for a in answers]

            # q_a = [t.xpath('string(.)').extract() for t in q_a]
            # q_a = self.keep_list_length(q_a, n_q_a)
            it['date'] = date
            it['doctor_id'] = doctor_id
            it['question'] =  ''.join(questions)
            it['answer'] =  ''.join(answers)
            # it['q1'] =  q_a[2] 
            # it['a1'] =  q_a[3] 
            # it['q2'] =  q_a[4] 
            # it['a2'] =  q_a[5] 
            # it['q3'] =  q_a[6] 
            # it['a3'] =  q_a[7] 
            it['q_id'] = self.q_id
            # aaa = it.load_item()
            # yield it.load_item()
            yield it
    def keep_list_length(self, target_list, target_length, filler=''):
        return target_list[:target_length] + [filler]*(target_length - len(target_list))