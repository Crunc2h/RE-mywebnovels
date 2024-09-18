import scrapy
import random
import cout.native.console as cout
from pathlib import Path
from fake_useragent import UserAgent

UA = UserAgent()
FILE_FORMAT = "html"
CHAPTER_LINK_PAGES_FORMAT = "/chapter_links_page-{current_page}.{file_format}"


class ChapterLinkPagesSpider(scrapy.Spider):
    name = "chapter_link_pages_spider"
    start_urls = []
    download_delay = 0.25
    custom_settings = {"USER_AGENT": UA.chrome}
    chapter_link_page_numbers_used = []

    def __init__(
        self,
        novel_page_urls_to_chapter_link_page_directories,
        get_chapters_index_page,
        get_next_page,
        *args,
        **kwargs,
    ):
        self.get_chapters_index_page = get_chapters_index_page
        self.get_next_page = get_next_page
        self.novel_page_urls_to_chapter_link_page_directories = (
            novel_page_urls_to_chapter_link_page_directories
        )
        self.cout = cout.ConsoleOut(header="SC_BOTS::CHAPTER_LINK_PAGES_SPIDER")
        self.start_urls.extend(
            list(novel_page_urls_to_chapter_link_page_directories.keys())
        )
        super().__init__(*args, **kwargs)
        self.cout.broadcast(style="success", message="Successfully initialized.")

    def parse(self, response):
        if response.url in self.start_urls:
            self.current_novel_page_url = response.url
            self.chapter_link_pages_directory = (
                self.novel_page_urls_to_chapter_link_page_directories[
                    self.current_novel_page_url
                ]
            )
            self.cout.broadcast(
                style="progress",
                message=f"Navigating to chapters index page of {self.current_novel_page_url}...",
            )
            yield response.follow(self.get_chapters_index_page(response), self.parse)
        else:
            self.cout.broadcast(
                style="progress",
                message=f"<{response.status}> Crawling {response.url}...",
            )

            rand_chapter_link_page_number = random.randint(0, 60000)
            while rand_chapter_link_page_number in self.chapter_link_page_numbers_used:
                rand_chapter_link_page_number = random.randint(0, 60000)
            self.chapter_link_page_numbers_used.append(rand_chapter_link_page_number)

            Path(
                self.chapter_link_pages_directory
                + CHAPTER_LINK_PAGES_FORMAT.format(
                    current_page=rand_chapter_link_page_number, file_format=FILE_FORMAT
                )
            ).write_bytes(response.body)

            next_page = self.get_next_page(response)
            if not next_page:
                self.cout.broadcast(
                    style="success",
                    message=f"Crawling of chapter link pages from {self.current_novel_page_url} is complete.",
                )
            else:
                yield response.follow(next_page, self.parse)
