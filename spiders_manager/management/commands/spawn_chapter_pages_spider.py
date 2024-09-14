import links_manager.models as lm_models
import spiders_manager.models as sm_models
from spiders_manager.models import (
    get_chapter_pages,
    process_chapter_pages,
    spawn_chapter_pages_spider,
)
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("novel_link", nargs="+", type=str)

    def handle(self, *args, **options):
        spider_instance = sm_models.SpiderInstanceProcess.objects.get(
            identifier=options["novel_link"][0]
        )
        spider_instance.state = sm_models.SpiderInstanceProcessState.IN_PROGRESS
        spider_instance.save()

        novel_link_object = lm_models.NovelLink.objects.get(
            link=options["novel_link"][0]
        )
        test = novel_link_object.get_uninitialized_chapter_links()[0]
        try:
            get_chapter_pages(
                chapter_pages_directory=novel_link_object.chapter_pages_directory,
                chapter_urls=test,
            )
        except Exception as ex:
            spider_instance.current_grace_period += 1
            spider_instance.save()
            if (
                spider_instance.current_grace_period
                >= spider_instance.maximum_grace_period
            ):
                spider_instance.state = (
                    sm_models.SpiderInstanceProcessState.EXTERNAL_ERROR
                )
                spider_instance.exception_message = str(ex)
                spider_instance.save()
                raise ex
            else:
                spider_instance.state = sm_models.SpiderInstanceProcessState.IDLE
                spider_instance.save()
                spawn_chapter_pages_spider(novel_link_object.link)
        try:
            process_chapter_pages(
                novel_link_object=novel_link_object,
                website_update_instance=spider_instance.website_update_instance,
            )
            spider_instance.state = sm_models.SpiderInstanceProcessState.FINISHED
            spider_instance.save()
        except Exception as ex:
            spider_instance.state = sm_models.SpiderInstanceProcessState.INTERNAL_ERROR
            spider_instance.exception_message = str(ex)
            spider_instance.save()
            raise ex
