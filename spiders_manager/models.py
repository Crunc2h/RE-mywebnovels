import os
import links_manager.models as lm_models
from django.db import models
from scrapy.crawler import CrawlerProcess
from sc_bots.sc_bots.spiders.novel_links_spider import NovelLinksSpider
from sc_bots.sc_bots.spiders.novel_pages_spider import NovelPagesSpider
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import subprocess


class SpiderConfig:
    pass


class Update(models.Model):
    processes_alive = models.IntegerField(default=0)
    processes_done = models.IntegerField(default=0)


def get_next_page(response):
    return response.css(".PagedList-skipToNext > a:nth-child(1)::attr(href)").get()


def get_max_page(response):
    return int(
        response.css(".PagedList-skipToLast > a:nth-child(1)::attr(href)")
        .get()
        .split("page=")[1]
    )


def get_name(url):
    return url.split("novel/")[1]


def get_novel_links(novel_link_pages_dir, crawler_start_link):
    process = CrawlerProcess()
    process.crawl(
        NovelLinksSpider,
        directory=novel_link_pages_dir,
        get_next_page=get_next_page,
        get_max_page=get_max_page,
        url=crawler_start_link,
    )
    process.start()


def get_novel_pages(urls, novel_pages_dir):
    process = CrawlerProcess()
    process.crawl(
        NovelPagesSpider,
        urls=urls,
        get_name=get_name,
        directory=novel_pages_dir,
    )
    process.start()


def spawn_novel_links_spider(site):
    os.system(
        "gnome-terminal -- "
        + f"bash -c 'cd workspace/personal_projects/REmywebnovels; source .re_venv/bin/activate; python3 manage.py novel_links_process '{site.crawler_start_link}' '{site.novel_link_pages_directory}'; exec bash'"
    )


def test_phase1():
    update_instance = Update()

    for site in lm_models.Website.objects.all():
        novel_link_pages = os.listdir(site.novel_link_pages_directory)
        for novel_link_page in novel_link_pages:
            with open(
                site.novel_link_pages_directory + "/" + novel_link_page, "r"
            ) as file:
                soup = BeautifulSoup(file, "lxml")
                links = [
                    site.link + novel_item.find("a")["href"]
                    for novel_item in soup.find_all(class_="novel-item")
                ]
                for link in links:
                    if not site.novel_link_exists(link):
                        new_link = lm_models.NovelLink(website=site, link=link)
                        new_link.save()
        links_updatable = [
            link for link in lm_models.NovelLink.objects.all() if link.is_updatable()
        ]
