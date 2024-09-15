import os
import links_manager.models as lm_models
import novels_storage.models as ns_models
import common
from bs4 import BeautifulSoup
from cout.native.common import standardize_str
from datetime import datetime


def process_novel_link_pages(
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
            novel_links_in_page, bad_content_in_page = novel_link_page_processor(
                soup, website_link_object
            )
            if bad_content_in_page and file_path not in bad_pages:
                bad_pages.append(file_path)
            new_novel_links.extend(novel_links_in_page)
    return new_novel_links, bad_pages


def process_chapter_link_pages(
    novel_link_object, chapter_link_pages_directory, bad_pages=[]
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
            chapter_links_in_page, bad_content_in_page = chapter_link_page_processor(
                soup
            )
            if bad_content_in_page and file_path not in bad_pages:
                bad_pages.append(file_path)
            new_chapter_links.extend(chapter_links_in_page)
    return new_chapter_links, bad_pages


def process_chapter_pages(novel_object, bad_pages=[]):
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
            chapters_in_page, bad_contents_in_page = chapter_page_processor(
                soup, novel_object
            )
            if bad_contents_in_page and file_path not in bad_pages:
                bad_pages.append(file_path)
            new_chapters.extend(chapters_in_page)
    return new_chapters, bad_pages


def process_novel_page(novel_directory, novel_page_format, file_format):
    file_path = novel_directory + novel_page_format.format(file_format=file_format)
    with open(file_path, "r") as file:
        soup = BeautifulSoup(file, "lxml")
        return novel_page_processor(soup)


def novel_link_page_processor(
    soup, website_link_object, get_novel_name_from_url=common.get_novel_name_from_url
):
    novel_links_in_page = []
    bad_content_in_page = False

    for novel_item in soup.find_all(class_="novel-item"):
        link_element = novel_item.find("a")
        if link_element != None:
            novel_links_in_page.append(
                lm_models.NovelLink(
                    webite_link=website_link_object,
                    link=website_link_object.base_link + link_element["href"],
                    name=get_novel_name_from_url(link_element["href"]),
                )
            )
        else:
            bad_content_in_page = True
    return novel_links_in_page, bad_content_in_page


def chapter_link_page_processor(soup, novel_link_object):
    chapter_links_in_page = []
    bad_content_in_page = False

    chapter_list = soup.select_one(".chapter-list")
    for chapter_item in chapter_list.find_all("li"):
        link_element = chapter_item.find("a")
        name_element = chapter_item.find(class_="chapter-title")
        if link_element != None and name_element != None:
            chapter_links_in_page.append(
                lm_models.ChapterLink(
                    novel_link=novel_link_object,
                    name=standardize_str(name_element.text),
                    link=novel_link_object.link + link_element["href"],
                )
            )
        else:
            bad_content_in_page = True
    return chapter_links_in_page, bad_content_in_page


def chapter_page_processor(
    soup,
    novel_object,
    get_chapter_number_from_title=common.get_chapter_number_from_title,
):
    name_element = soup.select_one(".chapter-title")
    date_published_element = soup.select_one(".titles > meta:nth-child(1)")
    chapter_container_element = soup.find(id="chapter-container")
    if (
        name_element != None
        and date_published_element != None
        and chapter_container_element != None
    ):
        name = standardize_str(name_element.text)
        number = get_chapter_number_from_title(name)
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

        return ns_models.Chapter(
            name=name,
            number=number,
            date_published=date_published,
            novel=novel_object,
            text=chapter_text,
        )
    return None


def novel_page_processor(soup):
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
