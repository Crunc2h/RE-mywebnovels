import spiders_manager.models as sm_models
import novels_storage.models as ns_models
from django.core.management.base import BaseCommand
from datetime import datetime, timezone
from spiders_manager.native.website_abstraction.website_interface import (
    WebsiteInterface,
)

WEBSITE_UPDATE_CYCLE_REFRESH_TIME = 0.5
BAD_PAGES_RETRY_COUNT_MAX = 5
NOVEL_UPDATE_CYCLE_REFRESH_TIME = 0.1


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("process_id", type=int)
        parser.add_argument("website_name", type=str)
        parser.add_argument("novel_page_urls", nargs="+", type=str)

    def handle(self, process_id, website_name, novel_page_urls, *args, **options):
        website = ns_models.Website.objects.get(name=website_name)
        website_interface = WebsiteInterface(
            process_id, website.name, caller=f"WEBSITE_UPDATE::{website.name.upper()}"
        )

        update_process_instance = website.update_instance.process_instances.get(
            process_id=process_id
        )

        update_process_instance.process_phase = sm_models.ProcessPhases.INITIALIZING
        update_process_instance.save()

        novel_link_objects = [
            website.link_object.get_novel_link_object_from_url(novel_page_url)
            for novel_page_url in novel_page_urls
        ]
        chapter_urls_to_chapter_page_directories = {}
        for novel_link_object in novel_link_objects:
            for chapter_link_object in novel_link_object.chapter_link_objects.all():
                chapter_urls_to_chapter_page_directories[chapter_link_object.link] = (
                    novel_link_object.novel.chapter_pages_directory
                )

        update_process_instance.process_phase = (
            sm_models.ProcessPhases.SCRAPING_CHAPTER_PAGES
        )
        update_process_instance.save()

        website_interface.get_chapter_pages(
            chapter_urls_to_chapter_page_directories=chapter_urls_to_chapter_page_directories
        )

        update_process_instance.process_phase = (
            sm_models.ProcessPhases.PROCESSING_CHAPTER_PAGES
        )
        update_process_instance.save()

        novel_link_objects_to_chapter_link_pages_directories = {}
        for novel_link_object in novel_link_objects:
            novel_link_objects_to_chapter_link_pages_directories[novel_link_object] = (
                novel_link_object.novel.chapter_link_pages_directory
            )

        matching_novel_and_chapters, bad_pages = (
            website_interface.process_chapter_pages(
                novel_objects=[
                    novel_link_object.novel for novel_link_object in novel_link_objects
                ]
            )
        )
        novels = []
        new_chapters = []
        for novel, chapters in matching_novel_and_chapters:
            novel.last_updated = datetime.now(timezone.utc)
            novel.is_being_updated = False
            novels.append(novel)
            new_chapters.extend(chapters)

        update_process_instance.process_phase = (
            sm_models.ProcessPhases.FILTERING_CHAPTER_LINK_DATA
        )
        update_process_instance.bad_content_found = len(bad_pages)
        if update_process_instance.bad_content_found > 0:
            update_process_instance.bad_content_file_paths = "\n".join(bad_pages)
        update_process_instance.save()

        ns_models.Novel.objects.bulk_update(
            novels, ["last_updated", "is_being_updated"]
        )
        ns_models.Chapter.objects.bulk_create(new_chapters)

        update_process_instance.process_phase = sm_models.ProcessPhases.FINISHED
        update_process_instance.save()
