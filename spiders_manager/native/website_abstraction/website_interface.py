import os
import novels_storage.models as ns_models
import cout.native.console as cout
import spiders_manager.models as sm_models
import spiders_manager.native.website_abstraction.webnovelpub.common as webnovelpub_common
import spiders_manager.native.website_abstraction.webnovelpub.processors as webnovelpub_processors
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
    def __init__(self, process_id, website_name, caller) -> None:
        self.process_id = process_id
        self.website_name = website_name

        self.update_process_instance = ns_models.Website.objects.get(
            name=self.website_name
        ).update_instance.process_instances.get(process_id=self.process_id)
        self.processor_instance = sm_models.UpdateProcessorInstance(
            update_process_instance=self.update_process_instance
        )
        self.processor_instance.save()

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
            self.get_max_page = webnovelpub_common.get_max_page
            self.get_chapters_index_page = webnovelpub_common.get_chapters_index_page
            self.get_novel_name_from_url = webnovelpub_common.get_novel_name_from_url

    def process_novel_link_pages(
        self,
        website_base_link,
        novel_link_pages_directory,
    ):
        self.cout.broadcast(
            style="init", message="Beginning to process novel link pages..."
        )

        novel_link_pages = os.listdir(novel_link_pages_directory)
        new_novel_link_object_dicts = []
        bad_pages = []

        for novel_link_page in novel_link_pages:
            file_path = novel_link_pages_directory + "/" + novel_link_page
            self.cout.broadcast(style="progress", message=f"Processing {file_path}...")

            with open(file_path, "r") as file:
                soup = BeautifulSoup(file, "lxml")
                novel_object_link_dicts_in_page, bad_content_in_page = (
                    self.novel_link_page_processor(soup, website_base_link)
                )
                if bad_content_in_page and file_path not in bad_pages:
                    bad_pages.append(file_path)

                new_novel_link_object_dicts.extend(novel_object_link_dicts_in_page)

        self.processor_instance.novel_link_pages_processed = len(novel_link_pages)
        self.processor_instance.save()

        return new_novel_link_object_dicts, bad_pages

    def process_chapter_link_pages(
        self, novel_link_objects_to_chapter_link_pages_directories
    ):
        self.cout.broadcast(
            style="init", message="Beginning to process chapter link pages..."
        )

        matching_novel_and_chapter_link_object_dicts = []
        bad_pages = []
        chapter_link_pages_processed = 0
        for (
            novel_link_object,
            chapter_link_pages_directory,
        ) in novel_link_objects_to_chapter_link_pages_directories.items():
            chapter_link_pages = os.listdir(chapter_link_pages_directory)
            new_chapter_link_object_dicts = []
            for chapter_link_page in chapter_link_pages:
                file_path = chapter_link_pages_directory + "/" + chapter_link_page
                self.cout.broadcast(
                    style="progress", message=f"Processing {file_path}..."
                )
                with open(file_path, "r") as file:
                    soup = BeautifulSoup(file, "lxml")
                    chapter_link_object_dicts_in_page, bad_content_in_page = (
                        self.chapter_link_page_processor(
                            soup, novel_link_object.website_link_object.base_link
                        )
                    )

                    new_chapter_link_object_dicts.extend(
                        chapter_link_object_dicts_in_page
                    )

                    if bad_content_in_page:
                        bad_pages.append(file_path)
            matching_novel_and_chapter_link_object_dicts.append(
                (novel_link_object, new_chapter_link_object_dicts)
            )
            chapter_link_pages_processed += len(chapter_link_pages)

        self.processor_instance.chapter_link_pages_processed = (
            chapter_link_pages_processed
        )
        self.processor_instance.save()
        return matching_novel_and_chapter_link_object_dicts, bad_pages

    def process_chapter_pages(self, novel_objects):
        self.cout.broadcast(
            style="init", message="Beginning to process chapter pages..."
        )
        matching_novel_and_chapters = []
        bad_pages = []
        chapter_pages_processed = 0
        for novel_object in novel_objects:
            chapter_pages = os.listdir(novel_object.chapter_pages_directory)
            new_chapters_of_novel = []
            for chapter_page in chapter_pages:
                file_path = novel_object.chapter_pages_directory + "/" + chapter_page
                self.cout.broadcast(
                    style="progress", message=f"Processing {file_path}..."
                )
                with open(file_path, "r") as file:
                    soup = BeautifulSoup(file, "lxml")
                    new_chapter = self.chapter_page_processor(soup, novel_object)
                    if new_chapter is None:
                        bad_pages.append(file_path)
                    else:
                        new_chapters_of_novel.append(new_chapter)
            matching_novel_and_chapters.append((novel_object, new_chapters_of_novel))
            chapter_pages_processed += len(chapter_pages)
        self.processor_instance.chapter_pages_processed = chapter_pages_processed
        self.processor_instance.save()
        return matching_novel_and_chapters, bad_pages

    def process_novel_pages(self, novel_objects, bad_pages=[]):
        self.cout.broadcast(style="init", message="Beginning to process novel pages...")

        matching_novels_and_novel_object_dicts = []
        bad_pages = []

        for novel_object in novel_objects:
            file_path = novel_object.novel_directory + NOVEL_PAGE_FORMAT.format(
                file_format="html"
            )
            self.cout.broadcast(style="progress", message=f"Processing {file_path}...")

            with open(file_path, "r") as file:
                soup = BeautifulSoup(file, "lxml")
                new_novel_object_dict = self.novel_page_processor(
                    soup, novel_object.name
                )
                if new_novel_object_dict is None:
                    bad_pages.append(file_path)
                else:
                    matching_novels_and_novel_object_dicts.append(
                        (novel_object, new_novel_object_dict)
                    )

        self.processor_instance.novel_pages_processed = len(novel_objects)
        self.processor_instance.save()

        return matching_novels_and_novel_object_dicts, bad_pages

    def get_novel_links(self, novel_link_pages_dir, crawler_start_link):
        self.cout.broadcast(
            style="init", message="Starting the novel link pages spider..."
        )
        crawler_process = CrawlerProcess()
        crawler_process.settings["LOG_ENABLED"] = True
        crawler_process.crawl(
            NovelLinkPagesSpider,
            process_id=self.process_id,
            website_name=self.website_name,
            novel_link_pages_directory=novel_link_pages_dir,
            website_crawler_start_url=crawler_start_link,
            get_next_page=self.get_next_page,
            get_max_page=self.get_max_page,
        )
        crawler_process.start()

    def get_chapter_links(self, novel_page_urls_to_chapter_link_page_directories):
        self.cout.broadcast(
            style="init", message="Starting the chapter link pages spider..."
        )
        process = CrawlerProcess()
        process.settings["LOG_ENABLED"] = True
        process.crawl(
            ChapterLinkPagesSpider,
            process_id=self.process_id,
            website_name=self.website_name,
            novel_page_urls_to_chapter_link_page_directories=novel_page_urls_to_chapter_link_page_directories,
            get_chapters_index_page=self.get_chapters_index_page,
            get_next_page=self.get_next_page,
            get_max_page=self.get_max_page,
        )
        process.start()

    def get_novel_pages(self, novel_page_urls_to_novel_directories):
        self.cout.broadcast(style="init", message="Starting the novel page spider...")
        process = CrawlerProcess()
        process.settings["LOG_ENABLED"] = True
        process.crawl(
            NovelPagesSpider,
            process_id=self.process_id,
            website_name=self.website_name,
            novel_page_urls_to_novel_directories=novel_page_urls_to_novel_directories,
        )
        process.start()

    def get_chapter_pages(self, chapter_urls_to_chapter_page_directories):
        self.cout.broadcast(
            style="init", message="Starting the chapter pages spider..."
        )
        process = CrawlerProcess()
        process.settings["LOG_ENABLED"] = True
        process.crawl(
            ChapterPagesSpider,
            process_id=self.process_id,
            website_name=self.website_name,
            chapter_urls_to_chapter_page_directories=chapter_urls_to_chapter_page_directories,
        )
        process.start()
