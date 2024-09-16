import novels_storage.models as ns_models
import links_manager.models as lm_models
import spiders_manager.models as sm_models
import spiders_manager.native.spawners as spawners
from spiders_manager.native.website_abstraction.website_interface import (
    WebsiteInterface,
)
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("website_name", nargs="+", type=str)
        parser.add_argument("novel_link", nargs="+", type=str)

    def handle(self, *args, **options):
        website = ns_models.Website.objects.get(name=options["website_name"][0])
        website_interface = WebsiteInterface(website.name)

        novel_link_object = website.link_object.novel_links.get(
            link=options["novel_link"][0]
        )

        spider_instance = sm_models.SpiderInstanceProcess.objects.get(
            identifier=novel_link_object.link
        )
        spider_instance.state = sm_models.SpiderInstanceProcessState.IN_PROGRESS
        spider_instance.save()

        try:
            website_interface.get_chapter_links(
                chapter_link_pages_dir=novel_link_object.novel.chapter_link_pages_directory,
                novel_page_url=novel_link_object.link,
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
                raise ex
            else:
                spider_instance.state = sm_models.SpiderInstanceProcessState.IDLE
                spider_instance.save()
                spawners.spawn_chapter_links_spider(
                    website.name, novel_link_object.link
                )

        try:
            new_chapter_links, bad_pages = website_interface.process_chapter_link_pages(
                novel_link_object=novel_link_object,
                chapter_link_pages_directory=novel_link_object.novel.chapter_link_pages_directory,
            )
            for new_chapter_link in new_chapter_links:
                if (
                    not novel_link_object.chapter_link_exists(new_chapter_link.link)
                    and novel_link_object.novel.get_chapter_of_name(
                        new_chapter_link.name
                    )
                    is None
                ):
                    new_chapter_link.save()
            if (
                len(bad_pages) > 0
                and spider_instance.current_processor_retry_on_bad_content
                < spider_instance.max_processor_retry_on_bad_content
            ):
                spider_instance.current_processor_retry_on_bad_content += 1
                spider_instance.save()
                spawners.spawn_chapter_links_spider(
                    website.name, novel_link_object.link
                )
                return
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
            raise ex
