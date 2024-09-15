import os
from spiders_manager.native.website_abstraction.website_interface import (
    WebsiteInterface,
)
from bs4 import BeautifulSoup


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
