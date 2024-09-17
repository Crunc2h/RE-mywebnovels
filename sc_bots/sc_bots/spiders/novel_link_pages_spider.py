import scrapy
import cout.native.console as cout
import spiders_manager.native.website_abstraction.process_signals as signals
from pathlib import Path
from fake_useragent import UserAgent

UA = UserAgent()
FILE_FORMAT = "html"
NOVEL_LINKS_PAGE_FORMAT = "/novel_links_page-{current_page}.{file_format}"


class NovelLinkPagesSpider(scrapy.Spider):
    name = "novel_link_pages_spider"
    start_urls = []
    max_page = None
    current_page = 0
    custom_settings = {"USER_AGENT": UA.chrome}

    def __init__(
        self,
        website_update_instance,
        novel_link_pages_directory,
        website_crawler_start_url,
        get_next_page,
        get_max_page,
        *args,
        **kwargs,
    ):
        self.website_update_instance = website_update_instance
        self.novel_link_pages_directory = novel_link_pages_directory
        self.get_next_page = get_next_page
        self.get_max_page = get_max_page
        self.start_urls.append(website_crawler_start_url)
        self.cout = cout.ConsoleOut(header="SC_BOTS::NOVEL_LINK_PAGES_SPIDER")
        self.cout.broadcast(style="success", message="Successfully initialized.")
        super().__init__(*args, **kwargs)

    def parse(self, response):
        self.cout.broadcast(
            style="progress",
            message=f"<{response.status}> Crawling {response.url}...",
        )
        if not self.max_page:
            self.max_page = self.get_max_page(response)
        if self.max_page == None:
            self.max_page = -1
        Path(
            self.novel_link_pages_directory
            + NOVEL_LINKS_PAGE_FORMAT.format(
                current_page=self.current_page, file_format=FILE_FORMAT
            )
        ).write_bytes(response.body)
        self.current_page += 1
        signals.novel_link_page_scraped.send(
            sender=None,
            instance=self.website_update_instance,
        )
        next_page = self.get_next_page(response)
        if not next_page:
            if self.current_page != self.max_page and self.max_page != -1:
                self.cout.broadcast(
                    style="failure",
                    message=f"Spider closed without extracting all content!",
                )
                raise Exception()
            self.cout.broadcast(
                style="success",
                message=f"Crawling of novel link pages is complete.",
            )
            return
        yield response.follow(next_page, self.parse)
