import spiders_manager.models as sm_models
import links_manager.models as lm_models
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
        parser.add_argument("process_id", type=int)
        parser.add_argument("website_name", type=str)

    def handle(self, process_id, website_name, *args, **options):

        website = ns_models.Website.objects.get(name=website_name)
        website_interface = WebsiteInterface(
            process_id,
            website.name,
            caller=f"{website.name.upper()}::NOVEL_LINK_PAGES_PROCESS",
        )

        update_process_instance = website.update_instance.process_instances.get(
            process_id=process_id
        )

        update_process_instance.process_phase = (
            sm_models.ProcessPhases.SCRAPING_NOVEL_LINK_PAGES
        )
        update_process_instance.save()

        website_interface.get_novel_links(
            website.novel_link_pages_directory, website.link_object.crawler_start_link
        )

        update_process_instance.process_phase = (
            sm_models.ProcessPhases.PROCESSING_NOVEL_LINK_PAGES
        )
        update_process_instance.save()

        new_novel_link_object_dicts, bad_pages = (
            website_interface.process_novel_link_pages(
                website_base_link=website.link_object.base_link,
                novel_link_pages_directory=website.novel_link_pages_directory,
            )
        )

        update_process_instance.process_phase = (
            sm_models.ProcessPhases.FILTERING_CHAPTER_LINK_DATA
        )
        update_process_instance.bad_content_found = len(bad_pages)
        if update_process_instance.bad_content_found > 0:
            update_process_instance.bad_content_file_paths = "\n".join(bad_pages)
        update_process_instance.save()

        matching_novels_and_dicts, absent_novel_link_object_dicts = (
            filter_existing_novel_links(
                new_novel_link_object_dicts, website.link_object
            )
        )

        novels_to_update = []
        novel_link_objects_to_save = []
        for novel, matching_novel_link_object_dict in matching_novels_and_dicts:
            novel.is_being_updated = True
            novels_to_update.append(novel)
            new_novel_link_object = lm_models.NovelLink(
                name=matching_novel_link_object_dict["name"],
                link=matching_novel_link_object_dict["link"],
                novel=novel,
                website_link_object=website.link_object,
            )
            novel_link_objects_to_save.append(new_novel_link_object)
        for novel_link_object_dict in absent_novel_link_object_dicts:
            new_novel = ns_models.Novel(
                name=novel_link_object_dict["name"],
                website=website,
                is_being_updated=True,
            )
            new_novel.save()
            new_novel_link_object = lm_models.NovelLink(
                name=novel_link_object_dict["name"],
                link=novel_link_object_dict["link"],
                website_link_object=website.link_object,
                novel=new_novel,
            )
            novel_link_objects_to_save.append(new_novel_link_object)

        ns_models.Novel.objects.bulk_update(novels_to_update, ["is_being_updated"])
        lm_models.NovelLink.objects.bulk_create(novel_link_objects_to_save)

        update_process_instance.bad_content_found = len(bad_pages)
        update_process_instance.novel_links_added = len(novel_link_objects_to_save)
        update_process_instance.process_phase = sm_models.ProcessPhases.FINISHED
        update_process_instance.save()


def filter_existing_novel_links(novel_link_object_dicts, website_link_object):
    absent_links = website_link_object.bulk_get_absent_novel_links(
        novel_link_object_dicts
    )
    return ns_models.bulk_dbwide_get_novels_of_name_by_nldicts(absent_links)
