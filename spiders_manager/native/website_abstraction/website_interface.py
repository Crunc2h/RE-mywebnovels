import novels_storage.models as ns_models
import cout.native.console as cout
import spiders_manager.native.website_abstraction.webnovelpub.common as webnovelpub_common
import spiders_manager.native.website_abstraction.webnovelpub.processors as webnovelpub_processors
import spiders_manager.native.website_abstraction.process_signals as signals
import os
from cout.native.common import standardize_str
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess
from sc_bots.sc_bots.spiders.novel_link_pages_spider import NovelLinkPagesSpider
from sc_bots.sc_bots.spiders.chapter_link_pages_spider import ChapterLinkPagesSpider
from sc_bots.sc_bots.spiders.novel_pages_spider import (
    NovelPagesSpider,
    NOVEL_PAGE_FORMAT,
)
from sc_bots.sc_bots.spiders.chapter_pages_spider import ChapterPagesSpider


class WebsiteInterface:
    def __init__(self, website_name, caller) -> None:
        self.cout = cout.ConsoleOut(header=f"{caller}::WEBSITE_INTERFACE")
        self.cout.broadcast(style="success", message="Successfully initialized.")
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
            self.get_chapters_index_page = webnovelpub_common.get_chapters_index_page
            self.get_novel_name_from_url = webnovelpub_common.get_novel_name_from_url

    def process_novel_link_pages(
        self,
        website_link_object,
        novel_link_pages_directory,
        bad_pages=[],
    ):
        self.cout.broadcast(
            style="init", message="Beginning to process novel link pages..."
        )
        if len(bad_pages) > 0:
            novel_link_pages = bad_pages
        else:
            novel_link_pages = os.listdir(novel_link_pages_directory)

        new_novel_links = []
        bad_pages = []

        for novel_link_page in novel_link_pages:
            file_path = novel_link_pages_directory + "/" + novel_link_page
            self.cout.broadcast(style="progress", message=f"Processing {file_path}...")
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
        self.cout.broadcast(
            style="init", message="Beginning to process chapter link pages..."
        )
        if len(bad_pages) > 0:
            chapter_link_pages = bad_pages
        else:
            chapter_link_pages = os.listdir(chapter_link_pages_directory)

        new_chapter_links = []
        bad_pages = []

        for chapter_link_page in chapter_link_pages:
            file_path = chapter_link_pages_directory + "/" + chapter_link_page
            self.cout.broadcast(style="progress", message=f"Processing {file_path}...")
            with open(file_path, "r") as file:
                soup = BeautifulSoup(file, "lxml")
                chapter_links_in_page, bad_content_in_page = (
                    self.chapter_link_page_processor(soup, novel_link_object)
                )
                signals.chapter_link_page_processed.send(
                    sender=None, instance=self.website_update_instance
                )
                if bad_content_in_page and file_path not in bad_pages:
                    bad_pages.append(file_path)
                new_chapter_links.extend(chapter_links_in_page)
        return new_chapter_links, bad_pages

    def process_chapter_pages(self, novel_object, bad_pages=[]):
        self.cout.broadcast(
            style="init", message="Beginning to process chapter pages..."
        )
        if len(bad_pages) > 0:
            chapter_pages = bad_pages
        else:
            chapter_pages = os.listdir(novel_object.chapter_pages_directory)

        new_chapters = []
        bad_pages = []

        for chapter_page in chapter_pages:
            file_path = novel_object.chapter_pages_directory + "/" + chapter_page
            self.cout.broadcast(style="progress", message=f"Processing {file_path}...")
            with open(file_path, "r") as file:
                soup = BeautifulSoup(file, "lxml")
                new_chapter = self.chapter_page_processor(soup, novel_object)
                signals.chapter_page_processed.send(
                    sender=None, instance=self.website_update_instance
                )
                if new_chapter is None:
                    bad_pages.append(file_path)
                else:
                    new_chapters.append(new_chapter)
        return new_chapters, bad_pages

    def process_novel_pages(self, novel_objects, bad_pages=[]):
        self.cout.broadcast(style="init", message="Beginning to process novel pages...")

        new_novels = []
        bad_pages = []

        for novel_object in novel_objects:
            file_path = novel_object.novel_directory + NOVEL_PAGE_FORMAT.format(
                file_format="html"
            )
            self.cout.broadcast(style="progress", message=f"Processing {file_path}...")
            with open(file_path, "r") as file:
                soup = BeautifulSoup(file, "lxml")
                new_novel, m2m_data = self.novel_page_processor(soup, novel_object.name)
                if new_novel is None:
                    bad_pages.append(file_path)
                else:
                    new_novels.append((new_novel, m2m_data))
        return new_novels, bad_pages

    def get_novel_links(self, novel_link_pages_dir, crawler_start_link):
        self.cout.broadcast(
            style="init", message="Starting the novel link pages spider..."
        )
        crawler_process = CrawlerProcess()
        crawler_process.settings["LOG_ENABLED"] = False
        crawler_process.crawl(
            NovelLinkPagesSpider,
            novel_link_pages_directory=novel_link_pages_dir,
            website_crawler_start_url=crawler_start_link,
            get_next_page=self.get_next_page,
        )
        crawler_process.start()

    def get_chapter_links(self, novel_page_urls_to_chapter_link_page_directories):
        self.cout.broadcast(
            style="init", message="Starting the chapter link pages spider..."
        )
        process = CrawlerProcess()
        process.settings["LOG_ENABLED"] = False
        process.crawl(
            ChapterLinkPagesSpider,
            novel_page_urls_to_chapter_link_page_directories=novel_page_urls_to_chapter_link_page_directories,
            get_chapters_index_page=self.get_chapters_index_page,
            get_next_page=self.get_next_page,
            get_max_page=self.get_max_page,
        )
        process.start()

    def get_novel_pages(self, novel_page_urls_to_novel_directories):
        self.cout.broadcast(style="init", message="Starting the novel page spider...")
        process = CrawlerProcess()
        process.settings["LOG_ENABLED"] = False
        process.crawl(
            NovelPagesSpider,
            novel_page_urls_to_novel_directories=novel_page_urls_to_novel_directories,
        )
        process.start()

    def get_chapter_pages(self, chapter_urls_to_chapter_page_directories):
        self.cout.broadcast(
            style="init", message="Starting the chapter pages spider..."
        )
        process = CrawlerProcess()
        process.settings["LOG_ENABLED"] = False
        process.crawl(
            ChapterPagesSpider,
            chapter_urls_to_chapter_page_directories=chapter_urls_to_chapter_page_directories,
        )
        process.start()
