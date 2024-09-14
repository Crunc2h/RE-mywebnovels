import spiders_manager.models as sm_models
import links_manager.models as lm_models
import novels_storage.models as ns_models
from django.core.management.base import BaseCommand
from spiders_manager.models import (
    get_novel_page,
    process_novel_page,
    spawn_novel_page_spider,
)
from datetime import datetime, timezone


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("novel_link", nargs="+", type=str)

    def handle(self, *args, **options):
        spider_instance = sm_models.SpiderInstanceProcess.objects.get(
            identifier=options["novel_link"][0]
        )
        spider_instance.state = sm_models.SpiderInstanceProcessState.IN_PROGRESS
        spider_instance.save()

        try:
            novel_link_object = lm_models.NovelLink.objects.get(
                link=options["novel_link"][0]
            )
        except Exception as ex:
            spider_instance.state = sm_models.SpiderInstanceProcessState.LAUNCH_ERROR
            spider_instance.exception_message = str(ex)
            spider_instance.save()
            return

        try:
            get_novel_page(
                novel_directory=novel_link_object.novel_directory,
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
                return
            else:
                spider_instance.state = sm_models.SpiderInstanceProcessState.IDLE
                spider_instance.save()
                spawn_novel_page_spider(novel_link_object.link)
                return

        try:
            novel = process_novel_page(novel_link_object=novel_link_object)
            if (
                novel is None
                and spider_instance.current_processor_retry_unverified_content_count
                < spider_instance.maximum_processor_retry_unverified_content_count
            ):
                spider_instance.current_processor_retry_unverified_content_count += 1
                spider_instance.save()
                spawn_novel_page_spider(novel_link_object.link)
                return
            elif (
                novel is None
                and spider_instance.current_processor_retry_unverified_content_count
                >= spider_instance.maximum_processor_retry_unverified_content_count
            ):
                spider_instance.state = sm_models.SpiderInstanceProcessState.BAD_CONTENT
                spider_instance.save()
                return
            else:
                if lm_models.db_novel_exists(novel.name):
                    matching_existing_novel = ns_models.Novel.objects.get(
                        name=novel.name
                    )
                    matching_existing_novel.completion_status = novel.completion_status
                    matching_existing_novel.summary = novel.summary
                    matching_existing_novel.save()
                    return
                else:
                    novel.save()

                novel_link_object.initialized = True
                novel_link_object.save()

                spider_instance.state = sm_models.SpiderInstanceProcessState.FINISHED
                spider_instance.save()
                return
        except Exception as ex:
            spider_instance.state = sm_models.SpiderInstanceProcessState.PROCESSOR_ERROR
            spider_instance.exception_message = str(ex)
            spider_instance.save()
            return
