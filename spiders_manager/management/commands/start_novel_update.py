import links_manager.models as lm_models
import spiders_manager.models as sm_models
from time import sleep
from spiders_manager.models import (
    spawn_chapter_links_spider,
    spawn_chapter_pages_spider,
    spawn_novel_page_spider,
)
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("website_name", nargs="+", type=str)
        parser.add_argument("novel_link", nargs="+", type=str)

    def handle(self, *args, **options):
        website = lm_models.Website.objects.get(name=options["website_name"][0])
        website_update_instance = website.update_instance

        spider_instance = sm_models.SpiderInstanceProcess(
            website_update_instance=website_update_instance,
            identifier=options["novel_link"][0],
        )
        spider_instance.save()

        novel_link_object = lm_models.NovelLink.objects.get(
            link=options["novel_link"][0]
        )

        spawn_chapter_links_spider(novel_link_object.link)
        while True:

            sleep(0.2)
            spider_instance = sm_models.SpiderInstanceProcess.objects.get(
                identifier=novel_link_object.link
            )
            if (
                spider_instance.state
                == sm_models.SpiderInstanceProcessState.SCRAPER_ERROR
                or spider_instance.state
                == sm_models.SpiderInstanceProcessState.PROCESSOR_ERROR
            ):
                return
            elif spider_instance.state == sm_models.SpiderInstanceProcessState.FINISHED:
                spider_instance.state = sm_models.SpiderInstanceProcessState.IDLE
                spider_instance.save()
                break

        spawn_novel_page_spider(novel_link_object.link)
        while True:

            sleep(0.2)
            spider_instance = sm_models.SpiderInstanceProcess.objects.get(
                identifier=novel_link_object.link
            )
            if (
                spider_instance.state
                == sm_models.SpiderInstanceProcessState.SCRAPER_ERROR
                or spider_instance.state
                == sm_models.SpiderInstanceProcessState.PROCESSOR_ERROR
            ):
                return
            elif spider_instance.state == sm_models.SpiderInstanceProcessState.FINISHED:
                spider_instance.state == sm_models.SpiderInstanceProcessState.IDLE
                spider_instance.save()
                break

        spawn_chapter_pages_spider(novel_link_object.link)
        while True:
            sleep(0.2)
            spider_instance = sm_models.SpiderInstanceProcess.objects.get(
                identifier=novel_link_object.link
            )
            if (
                spider_instance.state
                == sm_models.SpiderInstanceProcessState.SCRAPER_ERROR
                or spider_instance.state
                == sm_models.SpiderInstanceProcessState.PROCESSOR_ERROR
            ):
                return
            elif spider_instance.state == sm_models.SpiderInstanceProcessState.FINISHED:
                break
