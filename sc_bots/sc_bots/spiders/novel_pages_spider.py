from typing import Iterable
import scrapy
import cout.native.console as cout
from pathlib import Path
from fake_useragent import UserAgent

UA = UserAgent()
FILE_FORMAT = "html"
NOVEL_PAGE_FORMAT = "/novel_page.{file_format}"


class NovelPagesSpider(scrapy.Spider):
    name = "novel_pages_spider"
    start_urls = []
    custom_settings = {"USER_AGENT": UA.chrome}
    download_delay = 0.5

    def __init__(self, novel_page_urls_to_novel_directories, *args, **kwargs):
        self.novel_page_urls_to_novel_directories = novel_page_urls_to_novel_directories
        self.start_urls.extend(list(novel_page_urls_to_novel_directories.keys()))
        self.cout = cout.ConsoleOut(header="SC_BOTS::NOVEL_PAGES_SPIDER")
        super().__init__(*args, **kwargs)
        self.cout.broadcast(style="success", message="Successfully initialized.")

    def start_requests(self) -> Iterable[scrapy.Request]:
        super().start_requests()
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        current_novel_directory = self.novel_page_urls_to_novel_directories[
            response.url
        ]
        self.cout.broadcast(
            style="progress",
            message=f"<{response.status}> Crawling {response.url}...",
        )
        Path(
            current_novel_directory + NOVEL_PAGE_FORMAT.format(file_format=FILE_FORMAT)
        ).write_bytes(response.body)
