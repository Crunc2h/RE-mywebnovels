import links_manager.models as lm_models
import spiders_manager.models as sm_models
import novels_storage.models as ns_models
from time import sleep
from spiders_manager.models import (
    spawn_novel_links_spider,
    start_novel_update,
    get_novel_slug_name,
)
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("website_name", nargs="+", type=str)
        parser.add_argument("max_allowed_processes", nargs="+", type=int)

    def handle(self, *args, **options):
        lm_models.Website.objects.all().delete()
        sm_models.WebsiteUpdateInstance.objects.all().delete()
        sm_models.SpiderInstanceProcess.objects.all().delete()
        lm_models.NovelLink.objects.all().delete()
        lm_models.ChapterLink.objects.all().delete()
        ns_models.Chapter.objects.all().delete()
        ns_models.Novel.objects.all().delete()

        update_cycle = sm_models.UpdateCycle.objects.first()
        website = lm_models.Website(
            name="webnovelpub",
            link="www.webnovelpub.com",
            crawler_start_link="https://www.webnovelpub.pro/browse/genre-all-25060123/order-new/status-all",
        )
        website.save()

        website_update_instance = sm_models.WebsiteUpdateInstance(
            update_cycle=update_cycle,
            maximum_processes=options["max_allowed_processes"][0],
            website=website,
        )
        website_update_instance.save()
        """
        spider_instance = sm_models.SpiderInstanceProcess(
            website_update_instance=website_update_instance, identifier=website.name
        )
        spider_instance.save()

        spawn_novel_links_spider(website.name)
        while True:
            spider_instance = sm_models.SpiderInstanceProcess.objects.get(
                identifier=website.name
            )
            if (
                spider_instance.state
                == sm_models.SpiderInstanceProcessState.EXTERNAL_ERROR
                or spider_instance.state
                == sm_models.SpiderInstanceProcessState.INTERNAL_ERROR
            ):
                raise Exception(spider_instance.exception_message)
            elif spider_instance.state == sm_models.SpiderInstanceProcessState.FINISHED:
                website_update_instance.processes_finished += 1
                website_update_instance.save()
                spider_instance.delete()
                break
            sleep(0.2)
        
        print("fucking hey")
        links_updatable = [
            novel_link_object.link
            for novel_link_object in lm_models.NovelLink.objects.all()
            if novel_link_object.is_updatable()
        ]
        print("novel links created")
        """
        test = lm_models.NovelLink(
            website=website,
            link="https://www.webnovelpub.pro/novel/a-depressed-kendo-player-possesses-a-bastard-aristocrat",
            slug_name=get_novel_slug_name(
                "https://www.webnovelpub.pro/novel/a-depressed-kendo-player-possesses-a-bastard-aristocrat"
            ),
        )
        test.save()
        links_updatable = [test.link]
        while True:
            website_update_instance = sm_models.WebsiteUpdateInstance.objects.get(
                website=website
            )

            for (
                spider_process_instance
            ) in website_update_instance.spider_processes.all():
                if (
                    spider_process_instance.state
                    == sm_models.SpiderInstanceProcessState.EXTERNAL_ERROR
                    or spider_process_instance.state
                    == sm_models.SpiderInstanceProcessState.INTERNAL_ERROR
                ):
                    print(spider_process_instance.state)
                    print(spider_process_instance.exception_message)
                    return
                elif (
                    spider_process_instance.state
                    == sm_models.SpiderInstanceProcessState.FINISHED
                ):
                    spider_process_instance.delete()
                    website_update_instance.processes_finished += 1

            if len(links_updatable) == 0:
                break
            if (
                website_update_instance.spider_processes.count()
                < website_update_instance.maximum_processes
            ):
                print("spawning proc")
                updatable_link = links_updatable.pop()
                start_novel_update(website.name, updatable_link)
            sleep(0.2)
