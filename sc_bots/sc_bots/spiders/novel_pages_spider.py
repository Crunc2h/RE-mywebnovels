import scrapy
from pathlib import Path
from fake_useragent import UserAgent

UA = UserAgent()


class NovelPagesSpider(scrapy.Spider):
    name = "novel_pages_spider"
    start_urls = []
    custom_settings = {"USER_AGENT": UA.chrome}

    def __init__(self, directory, urls, get_name, *args, **kwargs):
        self.directory = directory
        self.get_name = get_name
        self.start_urls.extend(urls)
        super().__init__(*args, **kwargs)

    def parse(self, response):
        Path(
            self.directory + f"/novel_page-{self.get_name(response.url)}.html"
        ).write_bytes(response.body)
