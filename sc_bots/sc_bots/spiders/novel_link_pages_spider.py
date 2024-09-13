import scrapy
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
            + NOVEL_LINKS_PAGE_FORMAT.format(
                current_page=self.current_page, file_format=FILE_FORMAT
            )
        ).write_bytes(response.body)
        self.current_page += 1

        next_page = self.get_next_page(response)
        if not next_page:
            print(self.current_page)
            print(self.max_page)
            if self.current_page != self.max_page:
                raise Exception()
            return
        yield response.follow(next_page, self.parse)
