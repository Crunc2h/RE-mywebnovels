from typing import Iterable
import scrapy
from pathlib import Path
from fake_useragent import UserAgent

UA = UserAgent()
FILE_FORMAT = "html"
CHAPTER_PAGES_FORMAT = "/chapter-{current_chapter}.{file_format}"


class ChapterPagesSpider(scrapy.Spider):
    name = "chapter_pages_spider"
    start_urls = []
    custom_settings = {"USER_AGENT": UA.chrome}
    current_chapter = 1
    download_delay = 0.5

    def __init__(
        self,
        chapter_pages_directory,
        chapter_urls,
        *args,
        **kwargs,
    ):
        self.chapter_urls = chapter_urls
        self.chapter_pages_directory = chapter_pages_directory
        super().__init__(*args, **kwargs)

    def start_requests(self) -> Iterable[scrapy.Request]:
        for url in self.chapter_urls:
            yield scrapy.Request(url, callback=self.parse)
        return super().start_requests()

    def parse(self, response):

        Path(
            self.chapter_pages_directory
            + CHAPTER_PAGES_FORMAT.format(
                current_chapter=self.current_chapter, file_format=FILE_FORMAT
            )
        ).write_bytes(response.body)
        self.current_chapter += 1
