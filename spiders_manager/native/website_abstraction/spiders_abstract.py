from scrapy.crawler import CrawlerProcess
from sc_bots.sc_bots.spiders.novel_link_pages_spider import NovelLinkPagesSpider
from sc_bots.sc_bots.spiders.chapter_link_pages_spider import ChapterLinkPagesSpider
from sc_bots.sc_bots.spiders.novel_page_spider import NovelPageSpider
from sc_bots.sc_bots.spiders.chapter_pages_spider import ChapterPagesSpider
from spiders_manager.native.website_abstraction.website_interface import (
    WebsiteInterface,
)


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
