import scrapy
from pathlib import Path
from fake_useragent import UserAgent

UA = UserAgent()
FILE_FORMAT = "html"


class NovelLinkPagesSpider(scrapy.Spider):
    name = "novel_link_pages_spider"
    start_urls = []
    max_page = None
    current_page = 1
    custom_settings = {"USER_AGENT": UA.chrome}

    def __init__(
        self,
        novel_link_pages_directory,
        website_crawler_start_url,
        get_next_page,
        get_max_page,
        *args,
        **kwargs,
    ):
        self.novel_link_pages_directory = novel_link_pages_directory
        self.get_next_page = get_next_page
        self.get_max_page = get_max_page
        self.start_urls.append(website_crawler_start_url)
        super().__init__(*args, **kwargs)

    def parse(self, response):
        if not self.max_page:
            self.max_page = self.get_max_page(response)

        Path(
            self.novel_link_pages_directory
            + f"/novel_links_page-{self.current_page}.{FILE_FORMAT}"
        ).write_bytes(response.body)

        next_page = self.get_next_page(response)
        if not next_page:
            if self.current_page != self.max_page:
                raise Exception()
            return
        self.current_page += 1
        yield response.follow(next_page, self.parse)
