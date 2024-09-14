import links_manager.models as lm_models
import spiders_manager.models as sm_models
from spiders_manager.models import (
    get_novel_links,
    process_novel_link_pages,
    spawn_novel_links_spider,
)
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

        website_object = lm_models.Website.objects.get(name=options["website_name"][0])

        try:
            get_novel_links(
                novel_link_pages_dir=website_object.novel_link_pages_directory,
                crawler_start_link=website_object.crawler_start_link,
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
                spawn_novel_links_spider(website_object.name)
        try:
            process_novel_link_pages(
                website_object, spider_instance.website_update_instance
            )
            spider_instance.state = sm_models.SpiderInstanceProcessState.FINISHED
            spider_instance.save()
        except Exception as ex:
            spider_instance.state = sm_models.SpiderInstanceProcessState.PROCESSOR_ERROR
            spider_instance.exception_message = str(ex)
            spider_instance.save()
            raise ex
