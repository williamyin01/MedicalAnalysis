from scrapy.cmdline import execute

try:
    execute(
        [
            'scrapy',
            'crawl',
            # 'q_id_spider',
            # 'doctorSpider',
            # 'dxspider',
            'askspider',
            # '-o',
            # 'out.json',
        ]
    )
except SystemExit:
    pass