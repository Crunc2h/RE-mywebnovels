import scrapy
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
        chapter_link_pages_directory,
        get_next_page,
        get_max_page,
        novel_page_url,
        *args,
        **kwargs,
    ):
        self.chapter_link_pages_directory = chapter_link_pages_directory
        self.get_next_page = get_next_page
        self.get_max_page = get_max_page
        self.start_urls.append(novel_page_url)
        super().__init__(*args, **kwargs)

    def parse(self, response):
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
        next_page = self.get_next_page(response)
        if not next_page:
            if self.current_page != self.max_page and self.max_page != -1:
                raise Exception()
            return

        yield response.follow(next_page, self.parse)
