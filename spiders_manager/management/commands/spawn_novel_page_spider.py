import links_manager.models as lm_models
import novels_storage.models as ns_models
import spiders_manager.models as sm_models
import spiders_manager.native.spawners as spawners
from sc_bots.sc_bots.spiders.novel_page_spider import NOVEL_PAGE_FORMAT, FILE_FORMAT
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
        website_interface = WebsiteInterface(website_name=website.name)

        novel_link_object = website.link_object.novel_links.get(
            link=options["novel_link"][0]
        )
        novel = novel_link_object.novel

        spider_instance = sm_models.SpiderInstanceProcess.objects.get(
            identifier=options["novel_link"][0]
        )
        spider_instance.state = sm_models.SpiderInstanceProcessState.IN_PROGRESS
        spider_instance.save()

        try:
            website_interface.get_novel_page(
                novel_directory=novel.novel_directory,
                novel_page_url=novel_link_object.link,
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
                spawners.spawn_novel_page_spider(website.name, novel_link_object.link)
            return
        try:
            novel, m2m_data = website_interface.process_novel_page(
                novel_directory=novel.novel_directory,
                novel_page_format=NOVEL_PAGE_FORMAT,
                file_format=FILE_FORMAT,
            )
            if (
                novel is None
                and spider_instance.current_processor_retry_on_bad_content
                < spider_instance.max_processor_retry_on_bad_content
            ):
                spider_instance.current_processor_retry_on_bad_content += 1
                spider_instance.save()
                spawners.spawn_novel_page_spider(website.name, novel_link_object.link)
                return
            elif (
                novel is None
                and spider_instance.current_processor_retry_on_bad_content
                >= spider_instance.max_processor_retry_on_bad_content
            ):
                spider_instance.state = sm_models.SpiderInstanceProcessState.BAD_CONTENT
                spider_instance.save()
                return
            else:
                matching_existing_novel = ns_models.dbwide_get_novel_of_name(
                    novel_name=novel.name
                )
                if not matching_existing_novel.initialized:
                    for category in m2m_data["categories"]:
                        matching_existing_novel.categories.add(category)
                    for tag in m2m_data["tags"]:
                        matching_existing_novel.tags.add(tag)
                    matching_existing_novel.author = novel.author
                    matching_existing_novel.language = novel.language
                    matching_existing_novel.completion_status = novel.completion_status
                    matching_existing_novel.summary = novel.summary
                    matching_existing_novel.initialized = True
                else:
                    matching_existing_novel.completion_status = novel.completion_status
                    matching_existing_novel.summary = novel.summary

                matching_existing_novel.save()
                spider_instance.state = sm_models.SpiderInstanceProcessState.FINISHED
                spider_instance.save()
        except Exception as ex:
            spider_instance.state = sm_models.SpiderInstanceProcessState.PROCESSOR_ERROR
            spider_instance.exception_message = str(ex)
            spider_instance.save()
            raise ex
