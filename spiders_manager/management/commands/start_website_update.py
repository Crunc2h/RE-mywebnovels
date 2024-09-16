import links_manager.models as lm_models
import spiders_manager.models as sm_models
import novels_storage.models as ns_models
import spiders_manager.native.spawners as spawners
from time import sleep
from django.core.management.base import BaseCommand
from spiders_manager.native.website_abstraction.website_interface import (
    WebsiteInterface,
)

WEBSITE_UPDATE_CYCLE_REFRESH_TIME = 0.5
NOVEL_UPDATE_CYCLE_REFRESH_TIME = 0.1


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("website_name", nargs="+", type=str)
        parser.add_argument("max_allowed_processes", nargs="+", type=int)

    def handle(self, *args, **options):
        sm_models.UpdateCycle.objects.all().delete()
        sm_models.WebsiteUpdateInstance.objects.all().delete()
        sm_models.SpiderInstanceProcess.objects.all().delete()
        lm_models.NovelLink.objects.all().delete()
        lm_models.ChapterLink.objects.all().delete()
        ns_models.Website.objects.all().delete()
        ns_models.Chapter.objects.all().delete()
        ns_models.Novel.objects.all().delete()

        website = ns_models.Website(
            name="webnovelpub",
        )
        website.save()

        website_link_object = lm_models.WebsiteLink(
            website=website,
            base_link="https://www.webnovelworld.org",
            crawler_start_link="https://www.webnovelpub.pro/browse/genre-all-25060123/order-new/status-all",
        )
        website_link_object.save()

        update_cycle = sm_models.UpdateCycle(
            maximum_processes_per_site=options["max_allowed_processes"][0]
        )
        update_cycle.save()

        website_update_instance = sm_models.WebsiteUpdateInstance(
            update_cycle=update_cycle,
            maximum_processes=options["max_allowed_processes"][0],
            website=website,
        )
        website_update_instance.save()
        ##upper part is temp state restart
        ##if an error occurs while trying to access the initial variables then I wont be able to view it whatsoever
        # structure of the code needs a bit of rethinking...

        # sm_models.UpdateCycle.objects.all().delete()
        # sm_models.WebsiteUpdateInstance.objects.all().delete()
        # sm_models.WebsiteUpdateInstance.objects.all().delete()
        # sm_models.SpiderInstanceProcess.objects.all().delete()

        website = ns_models.Website.objects.get(name=options["website_name"][0])
        website_interface = WebsiteInterface(website.name)

        spider_instance = sm_models.SpiderInstanceProcess(
            website_update_instance=website_update_instance, identifier=website.name
        )
        spider_instance.save()

        spawners.spawn_novel_links_spider(website.name)
        while True:
            sleep(NOVEL_UPDATE_CYCLE_REFRESH_TIME)
            spider_instance = sm_models.SpiderInstanceProcess.objects.get(
                identifier=website.name
            )
            if (
                spider_instance.state
                == sm_models.SpiderInstanceProcessState.SCRAPER_ERROR
                or spider_instance.state
                == sm_models.SpiderInstanceProcessState.PROCESSOR_ERROR
                or spider_instance.state
                == sm_models.SpiderInstanceProcessState.BAD_CONTENT
            ):
                print(spider_instance.exception_message)
                print(spider_instance.bad_content_page_paths)
                return
            elif spider_instance.state == sm_models.SpiderInstanceProcessState.FINISHED:
                spider_instance.state = sm_models.SpiderInstanceProcessState.IDLE
                spider_instance.save()
                break

        novel_link_objects = website.link_object.novel_links.all()

        for novel_link_object in novel_link_objects:
            matching_novel = ns_models.dbwide_get_novel_of_name(
                website_interface.get_novel_name_from_url(novel_link_object.link)
            )
            if matching_novel != None:
                novel_link_object.novel = matching_novel
                novel_link_object.save()
                matching_novel.save()

        links_updatable = [
            novel_link.link
            for novel_link in novel_link_objects
            if novel_link.novel is None or novel_link.novel.is_updatable()
        ]
        links_updatable = links_updatable[0:50]
        errors = []
        while True:
            website_update_instance = sm_models.WebsiteUpdateInstance.objects.get(
                website=website
            )

            for spider_instance in website_update_instance.spider_processes.all():
                if (
                    spider_instance.state
                    == sm_models.SpiderInstanceProcessState.COMPLETE
                ):
                    spider_instance.delete()
                elif (
                    spider_instance.state
                    == sm_models.SpiderInstanceProcessState.BAD_CONTENT
                    or spider_instance.state
                    == sm_models.SpiderInstanceProcessState.PROCESSOR_ERROR
                    or spider_instance.state
                    == sm_models.SpiderInstanceProcessState.SCRAPER_ERROR
                ):
                    error = (
                        spider_instance.exception_message,
                        spider_instance.bad_content_page_paths,
                    )
                    if error not in errors:
                        errors.append(error)
            if (
                len(links_updatable) == 0
                or len(errors) > 0
                and website_update_instance.spider_processes.filter(
                    state=sm_models.SpiderInstanceProcessState.IN_PROGRESS
                ).count()
                == 0
            ):
                break
            if (
                website_update_instance.spider_processes.count()
                <= website_update_instance.maximum_processes
                and len(errors) == 0
            ):
                print("spawning proc")
                updatable_link = links_updatable.pop()
                spawners.start_novel_update(website.name, updatable_link)
            sleep(WEBSITE_UPDATE_CYCLE_REFRESH_TIME)

        for error in errors:
            print(error)
