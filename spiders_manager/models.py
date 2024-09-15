import os
import links_manager.models as lm_models
from django.db import models
from scrapy.crawler import CrawlerProcess
from sc_bots.sc_bots.spiders.novel_link_pages_spider import NovelLinkPagesSpider
from sc_bots.sc_bots.spiders.chapter_link_pages_spider import ChapterLinkPagesSpider
from sc_bots.sc_bots.spiders.novel_page_spider import NovelPageSpider
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
    SCRAPER_ERROR = "scraper_error"
    PROCESSOR_ERROR = "processor_error"
    LAUNCH_ERROR = "launch_error"
    IDLE = "idle"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    BAD_CONTENT = "bad_content"


class SpiderInstanceProcess(models.Model):
    website_update_instance = models.ForeignKey(
        WebsiteUpdateInstance, on_delete=models.CASCADE, related_name="spider_processes"
    )
    identifier = models.CharField(max_length=8096)
    state = models.CharField(max_length=64, default=SpiderInstanceProcessState.IDLE)
    maximum_scraper_grace_period = models.IntegerField(default=1)
    current_scraper_grace_period = models.IntegerField(default=0)
    maximum_processor_retry_unverified_content_count = models.IntegerField(default=1)
    current_processor_retry_unverified_content_count = models.IntegerField(default=0)
    bad_content = models.CharField(max_length=32128, blank=True, null=True)
    exception_message = models.CharField(max_length=4096, blank=True, null=True)


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
        chapter_link_pages_url=novel_page_url + "/chapters",
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
    process.start()


def spawn_novel_links_spider(website_name):
    os.system(
        "gnome-terminal -- "
        + f"bash -c 'source .re_venv/bin/activate; python3 manage.py spawn_novel_link_pages_spider '{website_name}'; exec bash'"
    )


def spawn_novel_page_spider(novel_link):
    os.system(
        "gnome-terminal -- "
        + f"bash -c 'source .re_venv/bin/activate; python3 manage.py spawn_novel_page_spider '{novel_link}'; exit;'"
    )


def spawn_chapter_links_spider(novel_link):
    os.system(
        "gnome-terminal -- "
        + f"bash -c 'source .re_venv/bin/activate; python3 manage.py spawn_chapter_link_pages_spider '{novel_link}'; exit;'"
    )


def spawn_chapter_pages_spider(novel_link):
    os.system(
        "gnome-terminal -- "
        + f"bash -c 'source .re_venv/bin/activate; python3 manage.py spawn_chapter_pages_spider '{novel_link}'; exec bash'"
    )


def start_novel_update(website_name, novel_link):
    os.system(
        "gnome-terminal -- "
        + f"bash -c 'source .re_venv/bin/activate; python3 manage.py start_novel_update '{website_name}' {novel_link}; exit;'"
    )


def start_website_update(website_name, max_allowed_processes):
    os.system(
        "gnome-terminal -- "
        + f"bash -c 'source .re_venv/bin/activate; python3 manage.py start_website_update '{website_name}' {max_allowed_processes};'"
    )
