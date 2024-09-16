import novels_storage.models as ns_models
from cout.native.common import standardize_str
import spiders_manager.native.website_abstraction.webnovelpub.common as webnovelpub_common
import spiders_manager.native.website_abstraction.webnovelpub.processors as webnovelpub_processors
import os
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess
from sc_bots.sc_bots.spiders.novel_link_pages_spider import NovelLinkPagesSpider
from sc_bots.sc_bots.spiders.chapter_link_pages_spider import ChapterLinkPagesSpider
from sc_bots.sc_bots.spiders.novel_page_spider import NovelPageSpider
from sc_bots.sc_bots.spiders.chapter_pages_spider import ChapterPagesSpider


class WebsiteInterface:
    def __init__(self, website_name) -> None:
        exists = ns_models.Website.objects.get(name=standardize_str(website_name))
        if website_name == "webnovelpub":
            self.novel_link_page_processor = (
                webnovelpub_processors.novel_link_page_processor
            )
            self.chapter_link_page_processor = (
                webnovelpub_processors.chapter_link_page_processor
            )
            self.novel_page_processor = webnovelpub_processors.novel_page_processor
            self.chapter_page_processor = webnovelpub_processors.chapter_page_processor
            self.get_next_page = webnovelpub_common.get_next_page
            self.get_max_page = webnovelpub_common.get_max_page
            self.get_chapters_index_page = webnovelpub_common.get_chapters_index_page
            self.get_novel_name_from_url = webnovelpub_common.get_novel_name_from_url

    def process_novel_link_pages(
        self,
        website_link_object,
        novel_link_pages_directory,
        bad_pages=[],
    ):
        if len(bad_pages) > 0:
            novel_link_pages = bad_pages
        else:
            novel_link_pages = os.listdir(novel_link_pages_directory)

        new_novel_links = []
        bad_pages = []

        for novel_link_page in novel_link_pages:
            file_path = novel_link_pages_directory + "/" + novel_link_page
            with open(file_path, "r") as file:
                soup = BeautifulSoup(file, "lxml")
                novel_links_in_page, bad_content_in_page = (
                    self.novel_link_page_processor(soup, website_link_object)
                )
                if bad_content_in_page and file_path not in bad_pages:
                    bad_pages.append(file_path)
                new_novel_links.extend(novel_links_in_page)
        return new_novel_links, bad_pages

    def process_chapter_link_pages(
        self, novel_link_object, chapter_link_pages_directory, bad_pages=[]
    ):
        if len(bad_pages) > 0:
            chapter_link_pages = bad_pages
        else:
            chapter_link_pages = os.listdir(chapter_link_pages_directory)

        new_chapter_links = []
        bad_pages = []

        for chapter_link_page in chapter_link_pages:
            file_path = chapter_link_pages_directory + "/" + chapter_link_page
            with open(file_path, "r") as file:
                soup = BeautifulSoup(file, "lxml")
                chapter_links_in_page, bad_content_in_page = (
                    self.chapter_link_page_processor(soup, novel_link_object)
                )
                if bad_content_in_page and file_path not in bad_pages:
                    bad_pages.append(file_path)
                new_chapter_links.extend(chapter_links_in_page)
        return new_chapter_links, bad_pages

    def process_chapter_pages(self, novel_object, bad_pages=[]):
        if len(bad_pages) > 0:
            chapter_pages = bad_pages
        else:
            chapter_pages = os.listdir(novel_object.chapter_pages_directory)

        new_chapters = []
        bad_pages = []

        for chapter_page in chapter_pages:
            file_path = novel_object.chapter_pages_directory + "/" + chapter_page
            with open(file_path, "r") as file:
                soup = BeautifulSoup(file, "lxml")
                new_chapter = self.chapter_page_processor(soup, novel_object)
                if new_chapter is None:
                    bad_pages.append(file_path)
                else:
                    new_chapters.append(new_chapter)
        return new_chapters, bad_pages

    def process_novel_page(self, novel_directory, novel_page_format, file_format):
        file_path = novel_directory + novel_page_format.format(file_format=file_format)
        with open(file_path, "r") as file:
            soup = BeautifulSoup(file, "lxml")
            return self.novel_page_processor(soup)

    def get_novel_links(self, novel_link_pages_dir, crawler_start_link):
        process = CrawlerProcess()
        process.crawl(
            NovelLinkPagesSpider,
            novel_link_pages_directory=novel_link_pages_dir,
            get_next_page=self.get_next_page,
            get_max_page=self.get_max_page,
            website_crawler_start_url=crawler_start_link,
        )
        process.start()

    def get_novel_page(self, novel_directory, novel_page_url):
        process = CrawlerProcess()
        process.crawl(
            NovelPageSpider,
            novel_page_url=novel_page_url,
            novel_directory=novel_directory,
        )
        process.start()

    def get_chapter_links(self, novel_page_url, chapter_link_pages_dir):
        process = CrawlerProcess()
        process.crawl(
            ChapterLinkPagesSpider,
            chapter_link_pages_directory=chapter_link_pages_dir,
            novel_page_url=novel_page_url,
            get_chapters_index_page=self.get_chapters_index_page,
            get_next_page=self.get_next_page,
            get_max_page=self.get_max_page,
        )
        process.start()

    def get_chapter_pages(self, chapter_urls, chapter_pages_directory):
        process = CrawlerProcess()
        process.crawl(
            ChapterPagesSpider,
            chapter_pages_directory=chapter_pages_directory,
            chapter_urls=chapter_urls,
        )
        process.start()
