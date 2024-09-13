import scrapy
from pathlib import Path
from fake_useragent import UserAgent

UA = UserAgent()
FILE_FORMAT = "html"
NOVEL_PAGE_FORMAT = "/novel_page.{file_format}"


class NovelPageSpider(scrapy.Spider):
    name = "novel_page_spider"
    start_urls = []
    custom_settings = {"USER_AGENT": UA.chrome}

    def __init__(self, novel_directory, novel_page_url, *args, **kwargs):
        self.novel_directory = novel_directory
        self.start_urls.append(novel_page_url)
        super().__init__(*args, **kwargs)

    def parse(self, response):
        Path(
            self.novel_directory + NOVEL_PAGE_FORMAT.format(file_format=FILE_FORMAT)
        ).write_bytes(response.body)
