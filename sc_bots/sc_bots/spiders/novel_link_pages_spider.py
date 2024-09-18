import scrapy
import cout.native.console as cout
from pathlib import Path
from fake_useragent import UserAgent

UA = UserAgent()
FILE_FORMAT = "html"
NOVEL_LINKS_PAGE_FORMAT = "/novel_links_page-{current_page}.{file_format}"


class NovelLinkPagesSpider(scrapy.Spider):
    name = "novel_link_pages_spider"
    start_urls = []
    current_page = 0
    custom_settings = {"USER_AGENT": UA.chrome}

    def __init__(
        self,
        novel_link_pages_directory,
        website_crawler_start_url,
        get_next_page,
        *args,
        **kwargs,
    ):
        self.novel_link_pages_directory = novel_link_pages_directory
        self.get_next_page = get_next_page
        self.cout = cout.ConsoleOut(header="SC_BOTS::NOVEL_LINK_PAGES_SPIDER")
        self.start_urls.append(website_crawler_start_url)
        super().__init__(*args, **kwargs)
        self.cout.broadcast(style="success", message="Successfully initialized.")

    def parse(self, response):
        self.cout.broadcast(
            style="progress",
            message=f"<{response.status}> Crawling {response.url}...",
        )

        Path(
            self.novel_link_pages_directory
            + NOVEL_LINKS_PAGE_FORMAT.format(
                current_page=self.current_page, file_format=FILE_FORMAT
            )
        ).write_bytes(response.body)

        self.current_page += 1
        next_page = self.get_next_page(response)
        if not next_page:
            self.cout.broadcast(
                style="success",
                message=f"Crawling of novel link pages is complete.",
            )
        else:
            yield response.follow(next_page, self.parse)
