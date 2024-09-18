import scrapy
import random
import cout.native.console as cout
from pathlib import Path
from fake_useragent import UserAgent

UA = UserAgent()
FILE_FORMAT = "html"
CHAPTER_PAGES_FORMAT = "/chapter-{current_chapter}.{file_format}"


class ChapterPagesSpider(scrapy.Spider):
    name = "chapter_pages_spider"
    start_urls = []
    custom_settings = {"USER_AGENT": UA.chrome}
    chapter_page_numbers_used = []
    download_delay = 0.5

    def __init__(
        self,
        chapter_urls_to_chapter_page_directories,
        *args,
        **kwargs,
    ):
        self.chapter_urls_to_chapter_page_directories = (
            chapter_urls_to_chapter_page_directories
        )
        self.start_urls.extend(list(chapter_urls_to_chapter_page_directories.keys()))
        self.cout = cout.ConsoleOut(header="SC_BOTS::CHAPTER_PAGES_SPIDER")
        super().__init__(*args, **kwargs)
        self.cout.broadcast(style="success", message="Successfully initialized.")

    def parse(self, response):
        current_chapter_pages_directory = self.chapter_urls_to_chapter_page_directories[
            response.url
        ]
        self.cout.broadcast(
            style="progress",
            message=f"<{response.status}> Crawling {response.url}...",
        )

        rand_chapter_page_number = random.randint(0, 60000)
        while rand_chapter_page_number in self.chapter_page_numbers_used:
            rand_chapter_page_number = random.randint(0, 60000)
        self.chapter_page_numbers_used.append(rand_chapter_page_number)

        Path(
            current_chapter_pages_directory
            + CHAPTER_PAGES_FORMAT.format(
                current_chapter=rand_chapter_page_number, file_format=FILE_FORMAT
            )
        ).write_bytes(response.body)
