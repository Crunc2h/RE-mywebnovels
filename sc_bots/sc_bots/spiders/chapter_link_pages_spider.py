import scrapy
import cout.native.console as cout
import spiders_manager.native.website_abstraction.process_signals as signals
from pathlib import Path
from fake_useragent import UserAgent

UA = UserAgent()
FILE_FORMAT = "html"
CHAPTER_LINK_PAGES_FORMAT = "/chapter_links_page-{current_page}.{file_format}"


class ChapterLinkPagesSpider(scrapy.Spider):
    name = "chapter_link_pages_spider"
    start_urls = []
    max_page = None
    current_page = 0
    custom_settings = {"USER_AGENT": UA.chrome}

    def __init__(
        self,
        website_update_instance,
        chapter_link_pages_directory,
        get_chapters_index_page,
        get_next_page,
        get_max_page,
        novel_page_url,
        *args,
        **kwargs,
    ):
        self.website_update_instance = website_update_instance
        self.chapter_link_pages_directory = chapter_link_pages_directory
        self.get_chapters_index_page = get_chapters_index_page
        self.novel_page_url = novel_page_url
        self.get_next_page = get_next_page
        self.get_max_page = get_max_page
        self.start_urls.append(novel_page_url)
        self.cout = cout.ConsoleOut(header="SC_BOTS::CHAPTER_LINK_PAGES_SPIDER")
        self.cout.broadcast(style="success", message="Successfully initialized.")
        super().__init__(*args, **kwargs)

    def parse(self, response):
        if response.url == self.novel_page_url:
            self.cout.broadcast(
                style="progress", message="Navigating to chapters index page..."
            )
            yield response.follow(self.get_chapters_index_page(response), self.parse)
        else:
            self.cout.broadcast(
                style="progress",
                message=f"<{response.status}> Crawling {response.url}...",
            )
            if not self.max_page:
                self.max_page = self.get_max_page(response)
            if self.max_page == None:
                self.max_page = -1
            Path(
                self.chapter_link_pages_directory
                + CHAPTER_LINK_PAGES_FORMAT.format(
                    current_page=self.current_page, file_format=FILE_FORMAT
                )
            ).write_bytes(response.body)
            self.current_page += 1
            signals.chapter_link_page_scraped.send(
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
                    message=f"Crawling of chapter link pages is complete.",
                )
                return
            yield response.follow(next_page, self.parse)
