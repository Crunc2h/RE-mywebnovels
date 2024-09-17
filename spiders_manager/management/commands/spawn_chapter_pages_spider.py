import links_manager.models as lm_models
import spiders_manager.models as sm_models
import novels_storage.models as ns_models
import spiders_manager.native.spawners as spawners
import spiders_manager.native.website_abstraction.process_signals as signals
from django.core.management.base import BaseCommand
from spiders_manager.native.website_abstraction.website_interface import (
    WebsiteInterface,
)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("website_name", nargs="+", type=str)
        parser.add_argument("novel_link", nargs="+", type=str)

    def handle(self, *args, **options):
        website = ns_models.Website.objects.get(name=options["website_name"][0])
        website_interface = WebsiteInterface(
            website.name, "SPIDER_PROCESS::CHAPTER_PAGES"
        )
        novel_link_object = lm_models.NovelLink.objects.get(
            link=options["novel_link"][0]
        )

        spider_instance = sm_models.SpiderInstanceProcess.objects.get(
            identifier=novel_link_object.link
        )
        spider_instance.state = sm_models.SpiderInstanceProcessState.IN_PROGRESS
        spider_instance.save()

        try:
            website_interface.get_chapter_pages(
                chapter_pages_directory=novel_link_object.novel.chapter_pages_directory,
                chapter_urls=[
                    chapter_link_object.link
                    for chapter_link_object in novel_link_object.chapter_links.all()
                ],
            )
        except Exception as ex:
            spider_instance.current_scraper_grace_period += 1
            signals.scraper_error.send(sender=None, instance=website.update_instance)
            if (
                spider_instance.current_scraper_grace_period
                >= spider_instance.maximum_scraper_grace_period
            ):
                spider_instance.state = (
                    sm_models.SpiderInstanceProcessState.SCRAPER_ERROR
                )
                spider_instance.exception_message = str(ex)
                spider_instance.save()
                signals.critical_error.send(
                    sender=None, instance=website.update_instance
                )
            else:
                spider_instance.state = sm_models.SpiderInstanceProcessState.IDLE
                spider_instance.save()
                spawners.spawn_chapter_pages_spider(
                    website.name, novel_link_object.link
                )
            return
        try:
            new_chapters, bad_pages = website_interface.process_chapter_pages(
                novel_object=novel_link_object.novel,
            )
            for new_chapter in new_chapters:
                if (
                    novel_link_object.novel.get_chapter_of_name(new_chapter.name)
                    is None
                ):
                    new_chapter.save()
                    signals.new_chapters_added.send(
                        sender=None, instance=website.update_instance
                    )
            if (
                len(bad_pages) > 0
                and spider_instance.current_processor_retry_on_bad_content
                < spider_instance.max_processor_retry_on_bad_content
            ):
                spider_instance.current_processor_retry_on_bad_content += 1
                signals.bad_content_error.send(
                    sender=None, instance=website.update_instance
                )
                spider_instance.save()
                spawners.spawn_chapter_pages_spider(
                    website.name, novel_link_object.link
                )
            elif (
                len(bad_pages) > 0
                and spider_instance.current_processor_retry_on_bad_content
                >= spider_instance.max_processor_retry_on_bad_content
            ):
                spider_instance.state = sm_models.SpiderInstanceProcessState.BAD_CONTENT
                signals.critical_error.send(
                    sender=None, instance=website.update_instance
                )
            else:
                spider_instance.state = sm_models.SpiderInstanceProcessState.FINISHED
            spider_instance.save()
        except Exception as ex:
            signals.critical_error.send(sender=None, instance=website.update_instance)
            spider_instance.state = sm_models.SpiderInstanceProcessState.PROCESSOR_ERROR
            spider_instance.exception_message = str(ex)
            spider_instance.save()
