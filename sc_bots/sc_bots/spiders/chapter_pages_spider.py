import scrapy
from pathlib import Path
from fake_useragent import UserAgent

UA = UserAgent()
FILE_FORMAT = "html"
CHAPTER_PAGES_FORMAT = "/chapter-{current_chapter}.{file_format}"


class ChapterPagesSpider(scrapy.Spider):
    name = "chapter_pages_spider"
    start_urls = []
    custom_settings = {"USER_AGENT": UA.chrome}
    current_chapter = 1

    def __init__(
        self,
        chapter_pages_directory,
        chapter_urls,
        *args,
        **kwargs,
    ):
        self.chapter_pages_directory = chapter_pages_directory
        self.start_urls.extend(chapter_urls)
        super().__init__(*args, **kwargs)

    def parse(self, response):
        Path(
            self.chapter_pages_directory
            + CHAPTER_PAGES_FORMAT.format(
                current_chapter=self.current_chapter, file_format=FILE_FORMAT
            )
        ).write_bytes(response.body)
        self.current_chapter += 1
