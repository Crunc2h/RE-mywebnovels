import links_manager.models as lm_models
import spiders_manager.models as sm_models
import novels_storage.models as ns_models
import spiders_manager.native.spawners as spawners
from time import sleep
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("website_name", nargs="+", type=str)
        parser.add_argument("novel_link", nargs="+", type=str)

    def handle(self, *args, **options):
        website = ns_models.Website.objects.get(name=options["website_name"][0])
        novel_link_object = website.link_object.novel_links.get(
            link=options["novel_link"][0]
        )
        spider_instance = sm_models.SpiderInstanceProcess(
            website_update_instance=website.update_instance,
            identifier=novel_link_object.link,
        )
        spider_instance.save()

        spawners.spawn_novel_page_spider(novel_link_object.link)
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

        spawners.spawn_chapter_links_spider(novel_link_object.link)
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

        spawners.spawn_chapter_pages_spider(novel_link_object.link)
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
