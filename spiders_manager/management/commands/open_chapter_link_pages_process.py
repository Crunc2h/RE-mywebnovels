import subprocess
import novels_storage.models as ns_models
from sc_bots.sc_bots.spiders.novel_pages_spider import NOVEL_PAGE_FORMAT
from django.core.management.base import BaseCommand
from spiders_manager.native.website_abstraction.website_interface import (
    WebsiteInterface,
)
from datetime import datetime, timezone

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
        novel_page_urls_to_chapter_link_page_directories = {}
        for novel_link_object in novel_link_objects:
            novel_page_urls_to_chapter_link_page_directories[novel_link_object.link] = (
                novel_link_object.novel.chapter_link_pages_directory
            )

        website_interface.get_chapter_links(
            novel_page_urls_to_chapter_link_page_directories=novel_page_urls_to_chapter_link_page_directories
        )

        novel_link_objects_to_chapter_link_pages_directories = {}
        for novel_link_object in novel_link_objects:
            novel_link_objects_to_chapter_link_pages_directories[novel_link_object] = (
                novel_link_object.novel.chapter_link_pages_directory
            )

        new_chapter_link_objects, bad_pages = (
            website_interface.process_chapter_link_pages(
                novel_link_objects_to_chapter_link_pages_directories=novel_link_objects_to_chapter_link_pages_directories
            )
        )

        for chapter_link_object in new_chapter_link_objects:
            if not chapter_link_object.novel_link.chapter_link_exists(
                chapter_link_object.link
            ):
                if (
                    chapter_link_object.novel_link.novel.get_chapter_of_name(
                        chapter_link_object.name
                    )
                    is None
                ):
                    chapter_link_object.save()

        args = [
            "python3",
            "manage.py",
            "open_chapter_pages_process",
            f"{website.name}",
        ]
        args.extend(novel_page_urls)

        chapter_pages_process = subprocess.run(
            args=args,
        )

        for novel_link_object in novel_link_objects:
            novel_link_object.novel.last_updated = datetime.now(timezone.utc)
            novel_link_object.novel.is_being_updated = False
            novel_link_object.novel.save()
