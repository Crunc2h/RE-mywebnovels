import scrapy
import cout.native.console as cout
import spiders_manager.native.website_abstraction.process_signals as signals
from pathlib import Path
from fake_useragent import UserAgent

UA = UserAgent()
FILE_FORMAT = "html"
NOVEL_PAGE_FORMAT = "/novel_page.{file_format}"


class NovelPageSpider(scrapy.Spider):
    name = "novel_page_spider"
    start_urls = []
    custom_settings = {"USER_AGENT": UA.chrome}

    def __init__(
        self, website_update_instance, novel_directory, novel_page_url, *args, **kwargs
    ):
        self.website_update_instance = website_update_instance
        self.novel_directory = novel_directory
        self.start_urls.append(novel_page_url)
        self.cout = cout.ConsoleOut(header="SC_BOTS::NOVEL_PAGE_SPIDER")
        self.cout.broadcast(style="success", message="Successfully initialized.")
        super().__init__(*args, **kwargs)

    def parse(self, response):
        self.cout.broadcast(
            style="progress",
            message=f"<{response.status}> Crawling {response.url}...",
        )
        Path(
            self.novel_directory + NOVEL_PAGE_FORMAT.format(file_format=FILE_FORMAT)
        ).write_bytes(response.body)
        signals.novel_page_scraped.send(
            sender=None, instance=self.website_update_instance
        )
