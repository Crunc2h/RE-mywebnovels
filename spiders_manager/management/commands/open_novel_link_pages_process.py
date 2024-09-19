import spiders_manager.models as sm_models
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

        new_novel_links, bad_pages = website_interface.process_novel_link_pages(
            website_link_object=website.link_object,
            novel_link_pages_directory=website.novel_link_pages_directory,
        )

        update_process_instance.process_phase = (
            sm_models.ProcessPhases.FILTERING_NOVEL_LINK_DATA
        )
        update_process_instance.save()

        website = ns_models.Website.objects.get(name=website.name)
        for new_novel_link in new_novel_links:
            if not website.link_object.novel_link_exists(new_novel_link.link):
                matching_novel = ns_models.dbwide_get_novel_of_name(new_novel_link.name)
                if matching_novel is None:
                    new_novel = ns_models.Novel(
                        name=new_novel_link.name, website=website
                    )
                    new_novel.is_being_updated = True
                    new_novel.save()
                    new_novel_link.novel = new_novel
                    new_novel_link.save()

                elif matching_novel.is_updatable():
                    matching_novel.is_being_updated = True
                    new_novel_link.novel = matching_novel
                    new_novel_link.save()
                    matching_novel.save()

                update_process_instance.novel_links_added += 1
                update_process_instance.save()

        update_process_instance.process_phase = sm_models.ProcessPhases.FINISHED
        update_process_instance.save()
