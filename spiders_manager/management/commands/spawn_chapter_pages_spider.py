import links_manager.models as lm_models
import spiders_manager.models as sm_models
from spiders_manager.models import (
    get_chapter_pages,
    process_chapter_pages,
    spawn_chapter_pages_spider,
)
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist


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
            get_chapter_pages(
                chapter_pages_directory=novel_link_object.chapter_pages_directory,
                chapter_urls=novel_link_object.get_uninitialized_chapter_links(),
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
                spawn_chapter_pages_spider(novel_link_object.link)
                return
        try:
            new_chapters, unverified_pages = process_chapter_pages(
                novel=novel_link_object,
                website_update_instance=spider_instance.website_update_instance,
            )
            for new_chapter in new_chapters:
                new_chapter.link.initialized = True
                new_chapter.save()
                new_chapter.link.save()
            if (
                len(unverified_pages) > 0
                and spider_instance.current_processor_retry_unverified_content_count
                < spider_instance.maximum_processor_retry_unverified_content_count
            ):
                spider_instance.current_processor_retry_unverified_content_count += 1
                spider_instance.save()
                spawn_chapter_pages_spider(novel_link_object.link)
                return
            elif (
                len(unverified_pages) > 0
                and spider_instance.current_processor_retry_unverified_content_count
                >= spider_instance.maximum_processor_retry_unverified_content_count
            ):
                spider_instance.state = sm_models.SpiderInstanceProcessState.BAD_CONTENT
                spider_instance.save()
                return
            else:
                spider_instance.state = sm_models.SpiderInstanceProcessState.FINISHED
                spider_instance.save()
                return
        except Exception as ex:
            spider_instance.state = sm_models.SpiderInstanceProcessState.PROCESSOR_ERROR
            spider_instance.exception_message = str(ex)
            spider_instance.save()
            return
