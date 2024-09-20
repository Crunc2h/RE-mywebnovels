import subprocess
import novels_storage.models as ns_models
import links_manager.models as lm_models
import spiders_manager.models as sm_models
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
        novel_page_urls_to_chapter_link_page_directories = {}
        for novel_link_object in novel_link_objects:
            novel_page_urls_to_chapter_link_page_directories[novel_link_object.link] = (
                novel_link_object.novel.chapter_link_pages_directory
            )

        update_process_instance.process_phase = (
            sm_models.ProcessPhases.SCRAPING_CHAPTER_LINK_PAGES
        )
        update_process_instance.save()

        website_interface.get_chapter_links(
            novel_page_urls_to_chapter_link_page_directories=novel_page_urls_to_chapter_link_page_directories
        )

        update_process_instance.process_phase = (
            sm_models.ProcessPhases.PROCESSING_CHAPTER_LINK_PAGES
        )
        update_process_instance.save()

        novel_link_objects_to_chapter_link_pages_directories = {}
        for novel_link_object in novel_link_objects:
            novel_link_objects_to_chapter_link_pages_directories[novel_link_object] = (
                novel_link_object.novel.chapter_link_pages_directory
            )

        matching_novel_and_chapter_link_object_dicts, bad_pages = (
            website_interface.process_chapter_link_pages(
                novel_link_objects_to_chapter_link_pages_directories=novel_link_objects_to_chapter_link_pages_directories
            )
        )

        update_process_instance.process_phase = (
            sm_models.ProcessPhases.FILTERING_CHAPTER_LINK_DATA
        )
        update_process_instance.bad_content_found = len(bad_pages)
        if update_process_instance.bad_content_found > 0:
            update_process_instance.bad_content_file_paths = "\n".join(bad_pages)
        update_process_instance.save()

        filtered = filter_existing_chapter_links(
            matching_novel_and_chapter_link_object_dicts=matching_novel_and_chapter_link_object_dicts,
            website_link_object=website.link_object,
        )
        chapter_link_objects_to_save = []
        chapter_links_added = 0

        for novel_link_object, chapter_link_object_dicts in filtered:
            new_chapter_link_objects = list(
                map(
                    lambda cl_obj_dict: lm_models.ChapterLink(
                        novel_link_object=novel_link_object,
                        name=cl_obj_dict["name"],
                        link=cl_obj_dict["link"],
                    ),
                    chapter_link_object_dicts,
                )
            )
            chapter_link_objects_to_save.extend(new_chapter_link_objects)
            chapter_links_added += len(new_chapter_link_objects)

        lm_models.ChapterLink.objects.bulk_create(chapter_link_objects_to_save)

        update_process_instance.chapter_links_added = chapter_links_added
        update_process_instance.process_phase = sm_models.ProcessPhases.IDLE
        update_process_instance.save()

        args = [
            "python3",
            "manage.py",
            "open_chapter_pages_process",
            f"{process_id}",
            f"{website.name}",
        ]
        args.extend(novel_page_urls)

        chapter_pages_process = subprocess.run(
            args=args,
        )


def filter_existing_chapter_links(
    matching_novel_and_chapter_link_object_dicts, website_link_object
):
    absent_nl_obj_and_cl_obj_dicts = website_link_object.bulk_get_absent_chapter_links(
        matching_novel_and_chapter_link_object_dicts
    )
    return ns_models.bulk_dbwide_filter_chapters_of_name_by_cldicts(
        absent_nl_obj_and_cl_obj_dicts
    )
