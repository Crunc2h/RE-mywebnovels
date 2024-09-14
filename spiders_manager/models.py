import os
import links_manager.models as lm_models
import novels_storage.models as ns_models
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
from datetime import datetime, timezone


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
    skip_last_link = response.css(
        ".PagedList-skipToLast > a:nth-child(1)::attr(href)"
    ).get()
    if skip_last_link != None:
        return skip_last_link.split("page=")[1]
    return None


def get_chapters_index_page(response):
    return response.css("a.grdbtn:nth-child(1)::attr(href)").get()


def get_novel_slug_name(url):
    return standardize_str(url.split("novel/")[1])


def get_novel_name_from_slug(slug_name):
    return standardize_str(" ".join(slug_name.split("-")))


def standardize_str(s):
    return s.strip().strip("\n").lower()


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
    print("testing gh contributions it doesnt seem to work properly")


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


def process_novel_link_pages(website_object, get_novel_slug_name, unverified_pages=[]):
    if len(unverified_pages) > 0:
        novel_link_pages = unverified_pages
    else:
        novel_link_pages = os.listdir(website_object.novel_link_pages_directory)

    new_novel_links = []
    unverified_pages = []

    for novel_link_page in novel_link_pages:
        file_path = website_object.novel_link_pages_directory + "/" + novel_link_page
        with open(file_path, "r") as file:
            soup = BeautifulSoup(file, "lxml")
            for novel_item in soup.find_all(class_="novel-item"):
                link_element = website_object.link + novel_item.find("a")
                if link_element != None:
                    new_novel_links.append(
                        lm_models.NovelLink(
                            webite=website_object,
                            link=link_element["href"],
                            slug_name=get_novel_slug_name(link_element["href"]),
                        )
                    )
                else:
                    if file_path not in unverified_pages:
                        unverified_pages.append(file_path)
    return new_novel_links, unverified_pages


def process_chapter_link_pages(novel_link_object, unverified_pages=[]):
    if len(unverified_pages) > 0:
        chapter_link_pages = unverified_pages
    else:
        chapter_link_pages = os.listdir(novel_link_object.chapter_link_pages_directory)

    new_chapter_links = []
    unverified_pages = []

    for chapter_link_page in chapter_link_pages:
        file_path = (
            novel_link_object.chapter_link_pages_directory + "/" + chapter_link_page
        )
        with open(file_path, "r") as file:
            soup = BeautifulSoup(file, "lxml")
            chapter_list = soup.select_one(".chapter-list")
            for chapter_item in chapter_list.find_all("li"):
                link_element = novel_link_object.website.link + chapter_item.find("a")
                name_element = chapter_item.find(class_="chapter-title")
                if link_element != None and name_element != None:
                    new_chapter_links.append(
                        lm_models.ChapterLink(
                            novel_link=novel_link_object,
                            name=standardize_str(name_element.text),
                            link=link_element["href"],
                        )
                    )
                else:
                    if file_path not in unverified_pages:
                        unverified_pages.append(file_path)
    return new_chapter_links, unverified_pages


def process_chapter_pages(novel_link_object, unverified_pages=[]):
    if len(unverified_pages) > 0:
        chapter_pages = unverified_pages
    else:
        chapter_pages = os.listdir(novel_link_object.chapter_pages_directory)

    new_chapters = []
    unverified_pages = []

    for chapter_page in chapter_pages:
        file_path = novel_link_object.chapter_pages_directory + "/" + chapter_page
        with open(file_path, "r") as file:
            soup = BeautifulSoup(file, "lxml")
            name_element = soup.select_one(".chapter-title")
            if name_element != None:
                name = standardize_str(name_element)
                matching_chapter_link_object = lm_models.ChapterLink.objects.get(
                    name_element
                )
            else:
                unverified_pages.append(file_path)
                continue

            date_published_element = soup.select_one(".titles > meta:nth-child(1)")
            chapter_container_element = soup.find(id="chapter-container")

            if date_published_element != None and chapter_container_element != None:
                number = standardize_str(name.split("Chapter ")[1].split(":")[0])
                date_published = datetime.strptime(
                    date_published_element["content"],
                    "%Y-%m-%dT%H:%M:%S",
                )
                chapter_text = "\n".join(
                    [
                        paragraph_element.text
                        for paragraph_element in chapter_container_element.find_all("p")
                    ]
                )
                new_chapters.append(
                    ns_models.Chapter(
                        name=name,
                        number=number,
                        link=matching_chapter_link_object,
                        date_published=date_published,
                        novel=novel_link_object.novel,
                        text=chapter_text,
                    )
                )
            else:
                unverified_pages.append(file_path)
    return new_chapters, unverified_pages


def process_novel_page(novel_link_object):
    file_path = novel_link_object.novel_directory + NOVEL_PAGE_FORMAT.format(
        file_format=FILE_FORMAT
    )
    with open(file_path, "r") as file:
        soup = BeautifulSoup(file, "lxml")
        name_element = soup.select_one(".novel-title")
        author_element = soup.select_one(
            ".header-stats > span:nth-child(1) > strong:nth-child(1) > i:nth-child(1)"
        )
        summary_element = soup.select_one("div.content")
        completion_status_element = soup.select_one(".completed")
        if completion_status_element is None:
            completion_status_element = soup.select_one(".ongoing")
        categories_element = soup.select_one(".categories")
        tags_element = soup.select_one(".tags")

        if (
            name_element
            and author_element
            and summary_element
            and completion_status_element
            and categories_element
            and tags_element
        ):
            name = standardize_str(name_element.text)
            author = ns_models.get_or_create_enum_model_from_str(
                standardize_str(author_element.text),
                ns_models.NovelAuthor,
            )
            summary = "\n".join(
                [
                    paragraph.text
                    for paragraph in soup.select_one("div.content").find_all("p")
                ]
            )
            completion_status = ns_models.get_or_create_enum_model_from_str(
                standardize_str(completion_status_element.text),
                ns_models.NovelCompletionStatus,
            )
            new_novel = ns_models.Novel(
                name=name,
                summary=summary,
                author=author,
                completion_status=completion_status,
                link=novel_link_object,
            )

            categories = [
                ns_models.get_or_create_enum_model_from_str(
                    standardize_str(category.text), ns_models.NovelCategory
                )
                for category in categories_element.find_all("li")
            ]
            tags = [
                ns_models.get_or_create_enum_model_from_str(
                    standardize_str(tag.text), ns_models.NovelTag
                )
                for tag in tags_element.find_all("li")
            ]

            for category in categories:
                new_novel.categories.add(category)
            for tag in tags:
                new_novel.tags.add(tag)

            return new_novel
        return None
