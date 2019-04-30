from scrapy.cmdline import execute

try:
    execute(
        [
            'scrapy',
            'crawl',
            'dxadv',
            # '-o',
            # 'out.json',
        ]
    )
except SystemExit:
    pass