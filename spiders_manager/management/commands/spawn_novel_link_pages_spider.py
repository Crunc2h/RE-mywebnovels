import novels_storage.models as ns_models
import spiders_manager.models as sm_models
import spiders_manager.native.spawners as spawners
from django.core.management.base import BaseCommand
from spiders_manager.native.website_abstraction.website_interface import (
    WebsiteInterface,
)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("website_name", nargs="+", type=str)

    def handle(self, *args, **options):
        website = ns_models.Website.objects.get(name=options["website_name"][0])
        website_interface = WebsiteInterface(website.name)

        spider_instance = sm_models.SpiderInstanceProcess.objects.get(
            identifier=website.name
        )
        spider_instance.state = sm_models.SpiderInstanceProcessState.IN_PROGRESS
        spider_instance.save()

        try:
            website_interface.get_novel_links(
                novel_link_pages_dir=website.novel_link_pages_directory,
                crawler_start_link=website.link_object.crawler_start_link,
            )
        except Exception as ex:
            spider_instance.current_scraper_grace_period += 1
            if (
                spider_instance.current_scraper_grace_period
                >= spider_instance.maximum_scraper_grace_period
            ):
                spider_instance.state = (
                    sm_models.SpiderInstanceProcessState.SCRAPER_ERROR
                )
                spider_instance.exception_message = str(ex)
                spider_instance.save()
            else:
                spider_instance.state = sm_models.SpiderInstanceProcessState.IDLE
                spider_instance.save()
                spawners.spawn_novel_links_spider(website.name)
            return
        try:
            new_novel_link_objects, bad_pages = (
                website_interface.process_novel_link_pages(
                    website.link_object,
                    website.novel_link_pages_directory,
                )
            )
            for new_novel_link_object in new_novel_link_objects:
                if not website.link_object.novel_link_exists(
                    new_novel_link_object.link
                ):
                    new_novel_link_object.save()
            if (
                len(bad_pages) > 0
                and spider_instance.current_processor_retry_on_bad_content
                < spider_instance.max_processor_retry_on_bad_content
            ):
                spider_instance.current_processor_retry_on_bad_content += 1
                spider_instance.state = sm_models.SpiderInstanceProcessState.IDLE
                spider_instance.save()
                spawners.spawn_novel_links_spider(website.name)
            elif (
                len(bad_pages) > 0
                and spider_instance.current_processor_retry_on_bad_content
                >= spider_instance.max_processor_retry_on_bad_content
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
