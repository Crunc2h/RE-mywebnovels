import links_manager.models as lm_models
import spiders_manager.models as sm_models
import novels_storage.models as ns_models
import spiders_manager.native.spawners as spawners
from time import sleep
from django.core.management.base import BaseCommand
from spiders_manager.native.website_abstraction.website_interface import (
    WebsiteInterface,
)


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
        """
        spider_instance = sm_models.SpiderInstanceProcess(
            website_update_instance=website_update_instance, identifier=website.name
        )
        spider_instance.save()

        spawners.spawn_novel_links_spider(website.name)
        while True:
            spider_instance = sm_models.SpiderInstanceProcess.objects.get(
                identifier=website.name
            )
            if (
                spider_instance.state
                == sm_models.SpiderInstanceProcessState.IN_PROGRESS
                or spider_instance.state == sm_models.SpiderInstanceProcessState.IDLE
            ):
                sleep(0.2)
                continue
            elif spider_instance.state == sm_models.SpiderInstanceProcessState.FINISHED:
                spider_instance.delete()
                break
            else:
                print(spider_instance.state)
                print(spider_instance.bad_content_page_paths)
                raise Exception(spider_instance.exception_message)

        novel_link_objects = website.link_object.novel_links.all()

        for novel_link_object in novel_link_objects:
            matching_novel = ns_models.dbwide_get_novel_of_name(
                website_interface.get_novel_name_from_url(novel_link_object.link)
            )
            if matching_novel != None:
                novel_link_object.novel = matching_novel
                novel_link_object.save()

        links_updatable = [
            novel_link.link
            for novel_link in novel_link_objects
            if novel_link.novel is None or novel_link.novel.is_updatable()
        ]
        """
        # test_links = [
        #    "https://www.webnovelpub.pro/novel/a-depressed-kendo-player-possesses-a-bastard-aristocrat",
        #    "https://www.webnovelpub.pro/novel/i-became-the-necromancer-of-the-academy",
        #    "https://www.webnovelpub.pro/novel/the-narrow-eyed-villain-of-the-demon-academy",
        #    "https://www.webnovelpub.pro/novel/i-became-an-immortal-on-mortal-realm",
        #    "https://www.webnovelpub.pro/novel/the-mirror-legacy",
        # ]
        test_links = [
            "https://www.webnovelpub.pro/novel/i-became-the-necromancer-of-the-academy"
        ]

        for link in test_links:
            t = lm_models.NovelLink(
                website_link=website_link_object,
                link=link,
                name=website_interface.get_novel_name_from_url(link),
            )
            t.save()
        links_updatable = [obj.link for obj in website.link_object.novel_links.all()]
        print(links_updatable)

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

            if len(links_updatable) == 0:
                break
            if (
                website_update_instance.spider_processes.count()
                < website_update_instance.maximum_processes
            ):
                print("spawning proc")
                updatable_link = links_updatable.pop()
                print(updatable_link)
                spawners.start_novel_update(website.name, updatable_link)
                break
            sleep(0.2)
