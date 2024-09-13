import os
import links_manager.models as lm_models
from django.db import models
from scrapy.crawler import CrawlerProcess
from sc_bots.sc_bots.spiders.novel_link_pages_spider import NovelLinkPagesSpider
from sc_bots.sc_bots.spiders.chapter_link_pages_spider import ChapterLinkPagesSpider
from sc_bots.sc_bots.spiders.novel_page_spider import NovelPageSpider
from sc_bots.sc_bots.spiders.chapter_pages_spider import ChapterPagesSpider
from bs4 import BeautifulSoup


class SpiderInstance(models.Model):
    identifier = models.CharField(max_length=8096)
    maximum_grace_period = models.IntegerField(default=5)
    current_grace_period = models.IntegerField(default=0)


def get_next_page(response):
    return response.css(".PagedList-skipToNext > a:nth-child(1)::attr(href)").get()


def get_max_page(response):
    return int(
        response.css(".PagedList-skipToLast > a:nth-child(1)::attr(href)")
        .get()
        .split("page=")[1]
    )


def get_chapters_index_page(response):
    return response.css(
        ".content-nav.grdbtn chapter-latest-container::attr(href)"
    ).get()


def get_novel_slug_name(url):
    return url.split("novel/")[1]


def get_novel_links(novel_link_pages_dir, crawler_start_link):
    process = CrawlerProcess()
    process.crawl(
        NovelLinkPagesSpider,
        directory=novel_link_pages_dir,
        get_next_page=get_next_page,
        get_max_page=get_max_page,
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


def get_chapter_links(novel_page_url, chapter_link_pages_dir):
    process = CrawlerProcess()
    process.crawl(
        ChapterLinkPagesSpider,
        chapter_link_pages_directory=chapter_link_pages_dir,
        novel_page_url=novel_page_url,
        get_chapters_index_page=get_chapters_index_page,
        get_next_page=get_next_page,
        get_max_page=get_max_page,
    )
    process.start()


def get_chapter_pages(chapter_pages_directory, chapter_urls):
    process = CrawlerProcess()
    process.crawl(
        ChapterPagesSpider,
        chapter_pages_directory=chapter_pages_directory,
        chapter_urls=chapter_urls,
    )


def spawn_novel_links_spider(website_name):
    os.system(
        "gnome-terminal -- "
        + f"bash -c 'cd workspace/personal_projects/REmywebnovels; source .re_venv/bin/activate; python3 manage.py spawn_novel_link_pages_spider '{website_name}'; exec bash'"
    )


def spawn_novel_page_spider(novel_link):
    os.system(
        "gnome-terminal -- "
        + f"bash -c 'cd workspace/personal_projects/REmywebnovels; source .re_venv/bin/activate; python3 manage.py spawn_novel_page_spider '{novel_link}'; exec bash'"
    )


def spawn_chapter_links_spider(novel_link):
    os.system(
        "gnome-terminal -- "
        + f"bash -c 'cd workspace/personal_projects/REmywebnovels; source .re_venv/bin/activate; python3 manage.py spawn_chapter_link_pages_spider '{novel_link}'; exec bash'"
    )


def spawn_chapter_pages_spider(novel_link):
    os.system(
        "gnome-terminal -- "
        + f"bash -c 'cd workspace/personal_projects/REmywebnovels; source .re_venv/bin/activate; python3 manage.py spawn_chapter_pages_spider '{novel_link}'; exec bash'"
    )


def process_novel_link_pages(website):
    novel_link_pages = os.listdir(website.novel_link_pages_directory)
    for novel_link_page in novel_link_pages:
        with open(
            website.novel_link_pages_directory + "/" + novel_link_page, "r"
        ) as file:
            soup = BeautifulSoup(file, "lxml")
            links = [
                website.link + novel_item.find("a")["href"]
                for novel_item in soup.find_all(class_="novel-item")
            ]
            for link in links:
                if not website.novel_link_exists(link):
                    new_link = lm_models.NovelLink(website=website, link=link)
                    new_link.save()
