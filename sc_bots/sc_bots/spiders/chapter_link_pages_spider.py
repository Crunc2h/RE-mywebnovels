import scrapy
from pathlib import Path
from fake_useragent import UserAgent

UA = UserAgent()
FILE_FORMAT = "html"


class ChapterLinkPagesSpider(scrapy.Spider):
    name = "chapter_link_pages_spider"
    start_urls = []
    max_page = None
    current_page = 1
    custom_settings = {"USER_AGENT": UA.chrome}

    def __init__(
        self,
        chapter_link_pages_directory,
        get_next_page,
        get_max_page,
        get_chapters_index_page,
        novel_page_url,
        *args,
        **kwargs,
    ):
        self.chapter_link_pages_directory = chapter_link_pages_directory
        self.novel_page_url = novel_page_url
        self.get_chapters_index_page = get_chapters_index_page
        self.get_next_page = get_next_page
        self.get_max_page = get_max_page
        self.start_urls.append(novel_page_url)
        super().__init__(*args, **kwargs)

    def parse(self, response):
        if response.url == self.novel_page_url:
            return response.follow(self.get_chapters_index_page(response), self.parse)
        if not self.max_page:
            self.max_page = self.get_max_page(response)

        Path(
            self.chapter_link_pages_directory
            + f"/chapter_links_page-{self.current_page}.{FILE_FORMAT}"
        ).write_bytes(response.body)

        next_page = self.get_next_page(response)
        if not next_page:
            if self.current_page != self.max_page:
                raise Exception()
            return
        self.current_page += 1
        yield response.follow(next_page, self.parse)
