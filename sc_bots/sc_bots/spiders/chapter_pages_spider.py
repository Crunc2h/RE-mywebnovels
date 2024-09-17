import scrapy
import cout.native.console as cout
import spiders_manager.native.website_abstraction.process_signals as signals
from typing import Iterable
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
        website_update_instance,
        chapter_pages_directory,
        chapter_urls,
        *args,
        **kwargs,
    ):
        self.website_update_instance = website_update_instance
        self.chapter_urls = chapter_urls
        self.chapter_pages_directory = chapter_pages_directory
        self.cout = cout.ConsoleOut(header="SC_BOTS::CHAPTER_PAGES_SPIDER")
        self.cout.broadcast(style="success", message="Successfully initialized.")
        super().__init__(*args, **kwargs)

    def start_requests(self) -> Iterable[scrapy.Request]:
        for url in self.chapter_urls:
            yield scrapy.Request(url, callback=self.parse)
        return super().start_requests()

    def parse(self, response):
        self.cout.broadcast(
            style="progress",
            message=f"<{response.status}> Crawling {response.url}...",
        )
        Path(
            self.chapter_pages_directory
            + CHAPTER_PAGES_FORMAT.format(
                current_chapter=self.current_chapter, file_format=FILE_FORMAT
            )
        ).write_bytes(response.body)
        self.current_chapter += 1
        signals.chapter_page_scraped.send(
            sender=None,
            instance=self.website_update_instance,
        )
