from scrapy.cmdline import execute

try:
    execute(
        [
            'scrapy',
            'crawl',
            'dxspider',
            # '-o',
            # 'out.json',
        ]
    )
except SystemExit:
    pass