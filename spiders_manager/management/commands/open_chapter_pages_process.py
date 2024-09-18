import novels_storage.models as ns_models
from django.core.management.base import BaseCommand
from spiders_manager.native.website_abstraction.website_interface import (
    WebsiteInterface,
)

WEBSITE_UPDATE_CYCLE_REFRESH_TIME = 0.5
BAD_PAGES_RETRY_COUNT_MAX = 5
NOVEL_UPDATE_CYCLE_REFRESH_TIME = 0.1


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("website_name", type=str)
        parser.add_argument("novel_page_urls", nargs="+", type=str)

    def handle(self, website_name, novel_page_urls, *args, **options):
        website = ns_models.Website.objects.get(name=website_name)
        website_interface = WebsiteInterface(
            website.name, caller=f"WEBSITE_UPDATE::{website.name.upper()}"
        )
        novel_link_objects = [
            website.link_object.get_novel_link_object_from_url(novel_page_url)
            for novel_page_url in novel_page_urls
        ]
        chapter_urls_to_chapter_page_directories = {}
        for novel_link_object in novel_link_objects:
            for chapter_link_object in novel_link_object.chapter_links.all():
                chapter_urls_to_chapter_page_directories[chapter_link_object.link] = (
                    novel_link_object.novel.chapter_pages_directory
                )

        website_interface.get_chapter_pages(
            chapter_urls_to_chapter_page_directories=chapter_urls_to_chapter_page_directories
        )

        novel_link_objects_to_chapter_link_pages_directories = {}
        for novel_link_object in novel_link_objects:
            novel_link_objects_to_chapter_link_pages_directories[novel_link_object] = (
                novel_link_object.novel.chapter_link_pages_directory
            )

        new_chapters, bad_pages = website_interface.process_chapter_pages(
            novel_objects=[
                novel_link_object.novel for novel_link_object in novel_link_objects
            ]
        )

        for new_chapter in new_chapters:
            new_chapter.save()
