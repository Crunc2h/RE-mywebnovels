import links_manager.models as lm_models
import novels_storage.models as ns_models
import spiders_manager.models as sm_models
from spiders_manager.native.website_abstraction.website_interface import (
    WebsiteInterface,
)
from spiders_manager.native.spawners import spawn_novel_links_spider
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("website_name", nargs="+", type=str)

    def handle(self, *args, **options):
        spider_instance = sm_models.SpiderInstanceProcess.objects.get(
            identifier=options["website_name"][0]
        )
        spider_instance.state = sm_models.SpiderInstanceProcessState.IN_PROGRESS
        spider_instance.save()

        try:
            website = ns_models.Website.objects.get(name=options["website_name"][0])
            website_interface = WebsiteInterface(website.name)
        except Exception as ex:
            spider_instance.state = sm_models.SpiderInstanceProcessState.LAUNCH_ERROR
            spider_instance.exception_message = str(ex)
            spider_instance.save()
            return

        try:
            website_interface.get_novel_links(
                novel_link_pages_dir=website.novel_link_pages_directory,
                crawler_start_link=website.link_object.crawler_start_link,
            )
        except Exception as ex:
            spider_instance.current_scraper_grace_period += 1
            spider_instance.save()
            if (
                spider_instance.current_scraper_grace_period
                >= spider_instance.maximum_scraper_grace_period
            ):
                spider_instance.state = (
                    sm_models.SpiderInstanceProcessState.SCRAPER_ERROR
                )
                spider_instance.exception_message = str(ex)
                spider_instance.save()
                return
            else:
                spider_instance.state = sm_models.SpiderInstanceProcessState.IDLE
                spider_instance.save()
                spawn_novel_links_spider(website.name)
        try:
            new_novel_links, bad_pages = website_interface.process_novel_link_pages(
                website.link_object, spider_instance.website_update_instance
            )
            for new_novel_link in new_novel_links:
                if not website.link_object.novel_link_exists(new_novel_link.link):
                    new_novel_link.save()

            if (
                len(bad_pages) > 0
                and spider_instance.current_processor_retry_unverified_content_count
                < spider_instance.maximum_processor_retry_unverified_content_count
            ):
                spider_instance.current_processor_retry_unverified_content_count += 1
                spider_instance.save()
                spawn_novel_links_spider(website.name)
                return
            elif (
                len(bad_pages) > 0
                and spider_instance.current_processor_retry_unverified_content_count
                >= spider_instance.maximum_processor_retry_unverified_content_count
            ):
                spider_instance.bad_content_page_paths = "\n".join(bad_pages)
                spider_instance.state = sm_models.SpiderInstanceProcessState.BAD_CONTENT
            else:
                spider_instance.state = sm_models.SpiderInstanceProcessState.FINISHED
            spider_instance.save()
        except Exception as ex:
            spider_instance.state = sm_models.SpiderInstanceProcessState.PROCESSOR_ERROR
            spider_instance.exception_message = str(ex)
            spider_instance.save()
