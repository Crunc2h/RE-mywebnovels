import spiders_manager.models as sm_models
import novels_storage.models as ns_models
import spiders_manager.native.spawners as spawners
import spiders_manager.native.website_abstraction.process_signals as signals
import cout.native.console as cout
from datetime import datetime, timezone
from django.core.management.base import BaseCommand
from time import sleep
from spiders_manager.native.website_abstraction.website_interface import (
    WebsiteInterface,
)
from spiders_manager.management.commands.start_website_update import (
    NOVEL_UPDATE_CYCLE_REFRESH_TIME,
)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("website_name", nargs="+", type=str)
        parser.add_argument("novel_link", nargs="+", type=str)

    def handle(self, *args, **options):

        website = ns_models.Website.objects.get(name=options["website_name"][0])
        c_out = cout.ConsoleOut(header=f"{website.name.upper()}_UPDATE::NOVEL_UPDATE")
        website_interface = WebsiteInterface(
            website.name, f"{website.name.upper()}_UPDATE::NOVEL_UPDATE"
        )

        novel_link_object = website.link_object.novel_links.get(
            link=options["novel_link"][0]
        )
        if novel_link_object.novel is None:
            novel = ns_models.Novel(
                website=website,
                name=website_interface.get_novel_name_from_url(novel_link_object.link),
            )
            novel.save()
            novel_link_object.novel = novel
            novel_link_object.save()
        else:
            novel = novel_link_object.novel
        novel.is_being_updated = True
        novel.save()

        spider_instance = sm_models.SpiderInstanceProcess(
            website_update_instance=website.update_instance,
            identifier=novel_link_object.link,
        )
        spider_instance.save()
        t_start = datetime.now(timezone.utc)
        c_out.broadcast(style="success", message="Launch successful.")
        c_out.broadcast(
            style="init", message=f"Beginning update on novel {novel.name.upper()}..."
        )
        c_out.broadcast(style="progress", message=f"Started update on novel page...")
        spawners.spawn_novel_page_spider(website.name, novel_link_object.link)
        while True:
            sleep(NOVEL_UPDATE_CYCLE_REFRESH_TIME)
            spider_instance = sm_models.SpiderInstanceProcess.objects.get(
                identifier=novel_link_object.link
            )
            if (
                spider_instance.state
                == sm_models.SpiderInstanceProcessState.SCRAPER_ERROR
                or spider_instance.state
                == sm_models.SpiderInstanceProcessState.PROCESSOR_ERROR
                or spider_instance.state
                == sm_models.SpiderInstanceProcessState.BAD_CONTENT
            ):
                c_out.broadcast(
                    style="failure",
                    message=f"Update on novel {novel.name.upper()} faced errors: {spider_instance.state.upper()}",
                )
                return
            elif spider_instance.state == sm_models.SpiderInstanceProcessState.FINISHED:
                spider_instance.state = sm_models.SpiderInstanceProcessState.IDLE
                spider_instance.save()
                c_out.broadcast(
                    style="success", message="Novel page is successfully updated."
                )
                break

        novel_link_object = website.link_object.novel_links.get(
            link=novel_link_object.link
        )
        c_out.broadcast(style="progress", message=f"Started update on chapter links...")
        spawners.spawn_chapter_links_spider(website.name, novel_link_object.link)
        while True:
            sleep(NOVEL_UPDATE_CYCLE_REFRESH_TIME)
            spider_instance = sm_models.SpiderInstanceProcess.objects.get(
                identifier=novel_link_object.link
            )
            if (
                spider_instance.state
                == sm_models.SpiderInstanceProcessState.SCRAPER_ERROR
                or spider_instance.state
                == sm_models.SpiderInstanceProcessState.PROCESSOR_ERROR
                or spider_instance.state
                == sm_models.SpiderInstanceProcessState.BAD_CONTENT
            ):
                c_out.broadcast(
                    style="failure",
                    message=f"Update on novel {novel.name.upper()} faced errors: {spider_instance.state.upper()}",
                )
                return
            elif spider_instance.state == sm_models.SpiderInstanceProcessState.FINISHED:
                spider_instance.state = sm_models.SpiderInstanceProcessState.IDLE
                spider_instance.save()
                c_out.broadcast(
                    style="success", message="Chapter links are successfully updated."
                )
                break

        novel_link_object = website.link_object.novel_links.get(
            link=novel_link_object.link
        )
        c_out.broadcast(style="progress", message=f"Started update on chapter pages...")
        spawners.spawn_chapter_pages_spider(website.name, novel_link_object.link)
        while True:
            sleep(NOVEL_UPDATE_CYCLE_REFRESH_TIME)
            spider_instance = sm_models.SpiderInstanceProcess.objects.get(
                identifier=novel_link_object.link
            )
            if (
                spider_instance.state
                == sm_models.SpiderInstanceProcessState.SCRAPER_ERROR
                or spider_instance.state
                == sm_models.SpiderInstanceProcessState.PROCESSOR_ERROR
                or spider_instance.state
                == sm_models.SpiderInstanceProcessState.BAD_CONTENT
            ):
                c_out.broadcast(
                    style="failure",
                    message=f"Update on novel {novel.name.upper()} faced errors: {spider_instance.state.upper()}",
                )
                return
            elif spider_instance.state == sm_models.SpiderInstanceProcessState.FINISHED:
                novel_link_object = website.link_object.novel_links.get(
                    link=novel_link_object.link
                )
                novel = novel_link_object.novel
                novel.is_being_updated = False
                novel.last_updated = datetime.now(timezone.utc)
                novel.save()

                spider_instance.state = sm_models.SpiderInstanceProcessState.COMPLETE
                spider_instance.save()
                c_out.broadcast(
                    style="success", message="Chapter pages are successfully updated."
                )
                c_out.broadcast(
                    style="init",
                    message=f"Update on novel {novel.name.upper()} is complete.",
                )
                t_delta = (datetime.now(timezone.utc) - t_start).seconds
                signals.process_finish.send(
                    sender=None, instance=website.update_instance, time=t_delta
                )
                return
