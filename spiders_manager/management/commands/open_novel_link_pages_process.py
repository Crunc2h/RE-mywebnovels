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
        parser.add_argument("website_name", nargs="+", type=str)

    def handle(self, *args, **options):
        website = ns_models.Website.objects.get(name=options["website_name"][0])
        website_interface = WebsiteInterface(
            website.name, caller=f"WEBSITE_UPDATE::{website.name.upper()}"
        )

        website_interface.get_novel_links(
            website.novel_link_pages_directory, website.link_object.crawler_start_link
        )

        new_novel_links, bad_pages = website_interface.process_novel_link_pages(
            website_link_object=website.link_object,
            novel_link_pages_directory=website.novel_link_pages_directory,
        )

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

        bad_pages_retry_counter = 0
        while (
            len(bad_pages) > 0 and bad_pages_retry_counter <= BAD_PAGES_RETRY_COUNT_MAX
        ):
            new_novel_links, bad_pages = website_interface.process_novel_link_pages(
                website_link_object=website.link_object,
                novel_link_pages_directory=website.novel_link_pages_directory,
            )

            website = ns_models.Website.objects.get(name=website.name)
            for new_novel_link in new_novel_links:
                if not website.link_object.novel_link_exists(new_novel_link.link):
                    matching_novel = ns_models.dbwide_get_novel_of_name(
                        new_novel_link.name
                    )
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

            bad_pages_retry_counter += 1

        if len(bad_pages) > 0:
            # do somtehing about it ffs
            pass
