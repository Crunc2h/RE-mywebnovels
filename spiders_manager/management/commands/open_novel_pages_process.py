import links_manager.models as lm_models
import novels_storage.models as ns_models
from sc_bots.sc_bots.spiders.novel_pages_spider import NOVEL_PAGE_FORMAT
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
        novel_page_urls_to_novel_directories = {}
        for novel_link_object in novel_link_objects:
            novel_page_urls_to_novel_directories[novel_link_object.link] = (
                novel_link_object.novel.novel_directory
            )

        website_interface.get_novel_pages(novel_page_urls_to_novel_directories)

        new_novels, bad_pages = website_interface.process_novel_pages(
            novel_objects=[
                novel_link_object.novel for novel_link_object in novel_link_objects
            ]
        )
        for new_novel, m2m in new_novels:
            matching_novel_object = website.link_object.novel_links.get(
                name=new_novel.name
            ).novel
            if not matching_novel_object.initialized:
                for category in m2m["categories"]:
                    matching_novel_object.categories.add(category)
                for tag in m2m["tags"]:
                    matching_novel_object.tags.add(tag)
                    matching_novel_object.author = new_novel.author
                    matching_novel_object.completion_status = (
                        new_novel.completion_status
                    )
                    matching_novel_object.summary = new_novel.summary
                    matching_novel_object.initialized = True
            else:
                matching_novel_object.completion_status = new_novel.completion_status
                matching_novel_object.summary = new_novel.summary
            matching_novel_object.save()
