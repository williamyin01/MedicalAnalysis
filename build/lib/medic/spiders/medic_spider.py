import scrapy

class medicSpider(scrapy.Spider):
    name = 'mdspider'
    allow_domains = ['120ask.com']
    start_urls = ['https://m.120ask.com/askg/posts_detail/990']
    custom_settings = {
        "USER_AGENT": 'Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
        "FEED_URI": 'result-120ask-test.csv',
        "FEED_FORMAT": 'CSV',
        'HTTPERROR_ALLOWED_CODES': [403, 404],
    }

    count = 0
    def parse(self, response):
        base_url = 'https://m.120ask.com/askg/posts_detail'
        q_a = response.css('div.g-under-askB p::text').getall()[:-1:2]
        q_id = int(response.request.url.split('/')[-1])
        if len(q_a) > 2:
            q_a = [a.strip() for a in q_a]
            question = q_a[0]
            answers = [x for x in q_a[1:] if  x != question]

            yield{
                'question': question,
                'answers': answers,
                'id': q_id,
            }
        if(q_id <= 2000 or self.count <= 50):
            q_id += 1
            next_href = base_url + '/' + str(q_id)
            self.count += 1
            yield scrapy.Request(next_href, self.parse)