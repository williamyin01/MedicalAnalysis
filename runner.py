from scrapy.cmdline import execute

try:
    execute(
        [
            'scrapy',
            'crawl',
            # 'q_id_spider',
            # 'doctorSpider',
            'dxspider',
            # '-o',
            # 'out.json',
        ]
    )
except SystemExit:
    pass