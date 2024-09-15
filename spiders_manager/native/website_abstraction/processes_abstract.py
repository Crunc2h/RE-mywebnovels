import os
from scrapy.crawler import CrawlerProcess
from sc_bots.sc_bots.spiders.novel_link_pages_spider import NovelLinkPagesSpider
from sc_bots.sc_bots.spiders.chapter_link_pages_spider import ChapterLinkPagesSpider
from sc_bots.sc_bots.spiders.novel_page_spider import NovelPageSpider
from sc_bots.sc_bots.spiders.chapter_pages_spider import ChapterPagesSpider
from spiders_manager.native.website_abstraction.website_interface import (
    WebsiteInterface,
)
from bs4 import BeautifulSoup


def get_novel_links(website_name, novel_link_pages_dir, crawler_start_link):
    website_interface = WebsiteInterface(website_name)
    process = CrawlerProcess()
    process.crawl(
        NovelLinkPagesSpider,
        novel_link_pages_directory=novel_link_pages_dir,
        get_next_page=website_interface.get_next_page,
        get_max_page=website_interface.get_max_page,
        website_crawler_start_url=crawler_start_link,
    )
    process.start()


def get_novel_page(novel_directory, novel_page_url):
    process = CrawlerProcess()
    process.crawl(
        NovelPageSpider,
        novel_page_url=novel_page_url,
        novel_directory=novel_directory,
    )
    process.start()


def get_chapter_links(website_name, novel_page_url, chapter_link_pages_dir):
    website_interface = WebsiteInterface(website_name)
    process = CrawlerProcess()
    process.crawl(
        ChapterLinkPagesSpider,
        chapter_link_pages_directory=chapter_link_pages_dir,
        novel_page_url=novel_page_url,
        get_chapters_index_page=website_interface.get_chapters_index_page,
        get_next_page=website_interface.get_next_page,
        get_max_page=website_interface.get_max_page,
    )
    process.start()


def get_chapter_pages(chapter_pages_directory, chapter_urls):
    process = CrawlerProcess()
    process.crawl(
        ChapterPagesSpider,
        chapter_pages_directory=chapter_pages_directory,
        chapter_urls=chapter_urls,
    )
    process.start()


def process_novel_link_pages(
    website_name,
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
            novel_links_in_page, bad_content_in_page = WebsiteInterface(
                website_name
            ).novel_link_page_processor(soup, website_link_object)
            if bad_content_in_page and file_path not in bad_pages:
                bad_pages.append(file_path)
            new_novel_links.extend(novel_links_in_page)
    return new_novel_links, bad_pages


def process_chapter_link_pages(
    website_name, novel_link_object, chapter_link_pages_directory, bad_pages=[]
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
            chapter_links_in_page, bad_content_in_page = WebsiteInterface(
                website_name
            ).chapter_link_page_processor(soup, novel_link_object)
            if bad_content_in_page and file_path not in bad_pages:
                bad_pages.append(file_path)
            new_chapter_links.extend(chapter_links_in_page)
    return new_chapter_links, bad_pages


def process_chapter_pages(website_name, novel_object, bad_pages=[]):
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
            chapters_in_page, bad_contents_in_page = WebsiteInterface(
                website_name
            ).chapter_page_processor(soup, novel_object)
            if bad_contents_in_page and file_path not in bad_pages:
                bad_pages.append(file_path)
            new_chapters.extend(chapters_in_page)
    return new_chapters, bad_pages


def process_novel_page(website_name, novel_directory, novel_page_format, file_format):
    file_path = novel_directory + novel_page_format.format(file_format=file_format)
    with open(file_path, "r") as file:
        soup = BeautifulSoup(file, "lxml")
        return WebsiteInterface(website_name).novel_page_processor(soup)
