import os
import links_manager.models as lm_models
from django.db import models
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
from sc_bots.sc_bots.spiders.novel_link_pages_spider import NovelLinkPagesSpider
from sc_bots.sc_bots.spiders.chapter_link_pages_spider import ChapterLinkPagesSpider
from sc_bots.sc_bots.spiders.novel_page_spider import (
    NovelPageSpider,
    FILE_FORMAT,
    NOVEL_PAGE_FORMAT,
)
from sc_bots.sc_bots.spiders.chapter_pages_spider import ChapterPagesSpider


class UpdateCycle(models.Model):
    t_start = models.DateTimeField(auto_now=True)
    maximum_processes = models.IntegerField()
    alive_processes = models.IntegerField(default=0)
    processes_finished = models.IntegerField(default=0)
    processes_in_progress = models.IntegerField(default=0)
    processes_error = models.IntegerField(default=0)

    current_novel_links = models.IntegerField(default=0)
    current_chapter_links = models.IntegerField(default=0)
    current_novels = models.IntegerField(default=0)
    current_chapters = models.IntegerField(default=0)

    new_novel_links_added = models.IntegerField(default=0)
    new_chapter_links_added = models.IntegerField(default=0)
    new_novels_added = models.IntegerField(default=0)
    new_chapters_added = models.IntegerField(default=0)

    novel_link_pages_processed = models.IntegerField(default=0)
    chapter_link_pages_processed = models.IntegerField(default=0)
    novel_pages_processed = models.IntegerField(default=0)
    chapter_pages_processed = models.IntegerField(default=0)


class WebsiteUpdateInstance(models.Model):
    t_start = models.DateTimeField(auto_now=True)
    update_cycle = models.ForeignKey(
        UpdateCycle, on_delete=models.CASCADE, related_name="website_update_instances"
    )
    website = models.OneToOneField(
        lm_models.Website, on_delete=models.CASCADE, related_name="update_instance"
    )
    maximum_processes = models.IntegerField()
    alive_processes = models.IntegerField(default=0)
    processes_finished = models.IntegerField(default=0)
    processes_in_progress = models.IntegerField(default=0)
    processes_error = models.IntegerField(default=0)

    current_of_novel_links = models.IntegerField(default=0)
    current_of_chapter_links = models.IntegerField(default=0)
    current_of_novels = models.IntegerField(default=0)
    current_of_chapters = models.IntegerField(default=0)

    new_novel_links_added = models.IntegerField(default=0)
    new_chapter_links_added = models.IntegerField(default=0)
    new_novels_added = models.IntegerField(default=0)
    new_chapters_added = models.IntegerField(default=0)

    novel_link_pages_processed = models.IntegerField(default=0)
    chapter_link_pages_processed = models.IntegerField(default=0)
    novel_pages_processed = models.IntegerField(default=0)
    chapter_pages_processed = models.IntegerField(default=0)


class SpiderInstanceProcessState:
    EXTERNAL_ERROR = "external_error"
    INTERNAL_ERROR = "internal_error"
    IDLE = "idle"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class SpiderInstanceProcess(models.Model):
    website_update_instance = models.ForeignKey(
        WebsiteUpdateInstance, on_delete=models.CASCADE, related_name="spider_processes"
    )
    identifier = models.CharField(max_length=8096)
    state = models.CharField(max_length=64, default=SpiderInstanceProcessState.IDLE)
    maximum_grace_period = models.IntegerField(default=1)
    current_grace_period = models.IntegerField(default=0)
    exception_message = models.CharField(max_length=4096, blank=True, null=True)


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
    return url.split("novel/")[1].lower()


def get_novel_name_from_slug(slug_name):
    return " ".join(slug_name.split("-")).lower()


def get_novel_links(novel_link_pages_dir, crawler_start_link):
    process = CrawlerProcess()
    process.crawl(
        NovelLinkPagesSpider,
        novel_link_pages_directory=novel_link_pages_dir,
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
        + f"bash -c 'source .re_venv/bin/activate; python3 manage.py spawn_novel_link_pages_spider '{website_name}'; exec bash'"
    )


def spawn_novel_page_spider(novel_link):
    os.system(
        "gnome-terminal -- "
        + f"bash -c 'source .re_venv/bin/activate; python3 manage.py spawn_novel_page_spider '{novel_link}'; exec bash'"
    )


def spawn_chapter_links_spider(novel_link):
    os.system(
        "gnome-terminal -- "
        + f"bash -c 'source .re_venv/bin/activate; python3 manage.py spawn_chapter_link_pages_spider '{novel_link}'; exec bash'"
    )


def spawn_chapter_pages_spider(novel_link):
    os.system(
        "gnome-terminal -- "
        + f"bash -c 'source .re_venv/bin/activate; python3 manage.py spawn_chapter_pages_spider '{novel_link}'; exec bash'"
    )


def start_novel_update(website_name, novel_link):
    os.system(
        "gnome-terminal -- "
        + f"bash -c 'source .re_venv/bin/activate; python3 manage.py start_novel_update '{website_name}' {novel_link}; exec bash'"
    )


def start_website_update(website_name, max_allowed_processes):
    os.system(
        "gnome-terminal -- "
        + f"bash -c 'source .re_venv/bin/activate; python3 manage.py start_website_update '{website_name}' {max_allowed_processes}; exec bash'"
    )


def process_novel_link_pages(website_object, website_update_instance):
    novel_link_pages = os.listdir(website_object.novel_link_pages_directory)
    for novel_link_page in novel_link_pages:
        with open(
            website_object.novel_link_pages_directory + "/" + novel_link_page, "r"
        ) as file:
            soup = BeautifulSoup(file, "lxml")
            novel_links = [
                website_object.link + novel_item.find("a")["href"]
                for novel_item in soup.find_all(class_="novel-item")
            ]
            for link in novel_links:
                if not website_object.novel_link_exists(link):
                    novel_slug_name = get_novel_slug_name(link)
                    novel_normal_name = get_novel_name_from_slug(novel_slug_name)
                    if not lm_models.db_novel_exists(
                        novel_normal_name=novel_normal_name,
                        novel_slug_name=novel_slug_name,
                    ):
                        new_link = lm_models.NovelLink(
                            website=website_object, link=link
                        )
                        new_link.save()

                        website_update_instance.new_novel_links_added += 1
                        website_update_instance.save()


def process_chapter_link_pages(novel_link_object, website_update_instance):
    chapter_link_pages = os.listdir(novel_link_object.chapter_link_pages_directory)
    for chapter_link_page in chapter_link_pages:
        with open(
            novel_link_object.chapter_link_pages_directory + "/" + chapter_link_page,
            "r",
        ) as file:
            soup = BeautifulSoup(file, "lxml")
            chapter_list = soup.select_one(class_="chapter-list")
            chapter_links = [
                chapter_item.find("a")["href"]
                for chapter_item in chapter_list.find_all("li")
            ]
            for link in chapter_links:
                if not novel_link_object.chapter_link_exists(link):
                    new_link = lm_models.ChapterLink(
                        novel_link=novel_link_object, link=link
                    )
                    new_link.save()

                    website_update_instance.new_novel_links_added += 1
                    website_update_instance.save()


def process_chapter_pages(novel_link_object, website_update_instance):
    chapter_pages = os.listdir(novel_link_object.chapter_pages_directory)
    for chapter_page in chapter_pages:
        with open(
            novel_link_object.chapter_pages_directory + "/" + chapter_page,
            "r",
        ) as file:
            soup = BeautifulSoup(file, "lxml")
            name = soup.select_one(".chapter-title").text
            date_published = soup.select_one(".titles > meta:nth-child(1)")[
                "content"
            ].strptime("%Y-%m-%dT%H:%M:%S")
            link = soup.select_one(".titles > meta:nth-child(3)")["content"]
            chapter_text = "\n".join(soup.find(id="chapter-container").find_all("p"))

            website_update_instance.new_chapter_links_added += 1
            website_update_instance.save()


def process_novel_page(novel_link_object, website_update_instance):
    with open(
        novel_link_object.novel_directory
        + NOVEL_PAGE_FORMAT.format(file_format=FILE_FORMAT),
        "r",
    ) as file:
        soup = BeautifulSoup(file, "lxml")
        name = soup.select_one(".novel-title").text
        completion_status = soup.select_one(".completed")
        if not completion_status:
            completion_status = soup.select_one(".ongoing").text
        else:
            completion_status = completion_status.text
        author = soup.select_one(
            "a.property-item:nth-child(2) > span:nth-child(1)"
        ).text
        print(name)
        print(completion_status)
