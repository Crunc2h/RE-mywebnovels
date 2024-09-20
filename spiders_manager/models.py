import novels_storage.models as ns_models
import cout.native.console as cout
from django.db import models


class ProcessPhases:
    IDLE = "IDLE"
    INITIALIZING = "INITIALIZING"
    FINISHED = "FINISHED"

    SCRAPING_NOVEL_LINK_PAGES = "SCRAPING NOVEL LINK PAGES"
    PROCESSING_NOVEL_LINK_PAGES = "PROCESSING NOVEL LINK PAGES"
    FILTERING_NOVEL_LINK_DATA = "FILTERING NOVEL LINK DATA"

    SCRAPING_NOVEL_PAGES = "SCRAPING NOVEL PAGES"
    PROCESSING_NOVEL_PAGES = "PROCESSING NOVEL PAGES"
    FILTERING_NOVEL_DATA = "FILTERING NOVEL DATA"

    SCRAPING_CHAPTER_LINK_PAGES = "SCRAPING CHAPTER LINK PAGES"
    PROCESSING_CHAPTER_LINK_PAGES = "PROCESSING CHAPTER LINK PAGES"
    FILTERING_CHAPTER_LINK_DATA = "FILTERING CHAPTER LINK DATA"

    SCRAPING_CHAPTER_PAGES = "SCRAPING CHAPTER PAGES"
    PROCESSING_CHAPTER_PAGES = "PROCESSING CHAPTER PAGES"
    FILTERING_CHAPTER_DATA = "FILTERING CHAPTER DATA"


class WebsiteUpdateInstance(models.Model):
    t_start = models.DateTimeField(auto_now=True)
    website = models.OneToOneField(
        ns_models.Website, on_delete=models.CASCADE, related_name="update_instance"
    )

    def __str__(self) -> str:
        processes_data = [
            process_instance.package_data()
            for process_instance in self.process_instances.all()
        ]
        process_headers = []
        sum_process_data = {
            "novel_links_added": 0,
            "chapter_links_added": 0,
            "chapters_added": 0,
            "new_novels_added": 0,
            "old_novels_updated": 0,
            "novels_update_process_finished": 0,
            "novel_link_pages_scraped": 0,
            "chapter_link_pages_scraped": 0,
            "novel_pages_scraped": 0,
            "chapter_pages_scraped": 0,
            "novel_link_pages_processed": 0,
            "chapter_link_pages_processed": 0,
            "novel_pages_processed": 0,
            "chapter_pages_processed": 0,
        }
        for process_data in processes_data:
            process_headers.append(
                (process_data["process_id"], process_data["process_phase"])
            )
            sum_process_data["novel_links_added"] += process_data["novel_links_added"]
            sum_process_data["chapter_links_added"] += process_data[
                "chapter_links_added"
            ]
            sum_process_data["chapters_added"] += process_data["chapters_added"]
            sum_process_data["new_novels_added"] += process_data["new_novels_added"]
            sum_process_data["old_novels_updated"] += process_data["old_novels_updated"]
            sum_process_data["novels_update_process_finished"] += process_data[
                "novels_update_process_finished"
            ]
            sum_process_data["novel_link_pages_scraped"] += process_data[
                "novel_link_pages_scraped"
            ]
            sum_process_data["chapter_link_pages_scraped"] += process_data[
                "chapter_link_pages_scraped"
            ]
            sum_process_data["novel_pages_scraped"] += process_data[
                "novel_pages_scraped"
            ]
            sum_process_data["chapter_pages_scraped"] += process_data[
                "chapter_pages_scraped"
            ]
            sum_process_data["novel_link_pages_processed"] += process_data[
                "novel_link_pages_processed"
            ]
            sum_process_data["chapter_link_pages_processed"] += process_data[
                "chapter_link_pages_processed"
            ]
            sum_process_data["novel_pages_processed"] += process_data[
                "novel_pages_processed"
            ]
            sum_process_data["chapter_pages_processed"] += process_data[
                "chapter_pages_processed"
            ]
        return cout.ConsoleOut.website_update_display(
            self.t_start, process_headers, sum_process_data
        )


class UpdateProcessInstance(models.Model):
    process_id = models.IntegerField()
    process_phase = models.CharField(max_length=256, default=ProcessPhases.IDLE)

    novel_links_added = models.IntegerField(default=0)
    chapter_links_added = models.IntegerField(default=0)
    chapters_added = models.IntegerField(default=0)

    new_novels_added = models.IntegerField(default=0)
    old_novels_updated = models.IntegerField(default=0)
    novels_update_process_finished = models.IntegerField(default=0)

    scraper_errors_faced = models.IntegerField(default=0)
    bad_content_found = models.IntegerField(default=0)
    bad_content_file_paths = models.TextField(max_length=256000, default="")

    t_start = models.DateTimeField(auto_now=True)
    website_update_instance = models.ForeignKey(
        WebsiteUpdateInstance,
        on_delete=models.CASCADE,
        related_name="process_instances",
    )

    def package_data(self):
        (
            novel_link_pages_scraped,
            chapter_link_pages_scraped,
            novel_pages_scraped,
            chapter_pages_scraped,
        ) = self.get_all_spider_instance_data()

        (
            novel_link_pages_processed,
            chapter_link_pages_processed,
            novel_pages_processed,
            chapter_pages_processed,
        ) = self.get_all_processor_instance_data()

        return {
            "process_id": self.process_id,
            "process_phase": self.process_phase,
            "novel_links_added": self.novel_links_added,
            "chapter_links_added": self.chapter_links_added,
            "chapters_added": self.chapters_added,
            "new_novels_added": self.new_novels_added,
            "old_novels_updated": self.old_novels_updated,
            "novels_update_process_finished": self.novels_update_process_finished,
            "novel_link_pages_scraped": novel_link_pages_scraped,
            "chapter_link_pages_scraped": chapter_link_pages_scraped,
            "novel_pages_scraped": novel_pages_scraped,
            "chapter_pages_scraped": chapter_pages_scraped,
            "novel_link_pages_processed": novel_link_pages_processed,
            "chapter_link_pages_processed": chapter_link_pages_processed,
            "novel_pages_processed": novel_pages_processed,
            "chapter_pages_processed": chapter_pages_processed,
        }

    def get_all_spider_instance_data(self):
        novel_link_pages_scraped = 0
        chapter_link_pages_scraped = 0
        novel_pages_scraped = 0
        chapter_pages_scraped = 0
        for spider_instance in self.spider_instances.all():
            novel_link_pages_scraped += spider_instance.novel_link_pages_scraped
            chapter_link_pages_scraped += spider_instance.chapter_link_pages_scraped
            novel_pages_scraped += spider_instance.novel_pages_scraped
            chapter_pages_scraped += spider_instance.chapter_pages_scraped
        return (
            novel_link_pages_scraped,
            chapter_link_pages_scraped,
            novel_pages_scraped,
            chapter_pages_scraped,
        )

    def get_all_processor_instance_data(self):
        novel_link_pages_processed = 0
        chapter_link_pages_processed = 0
        novel_pages_processed = 0
        chapter_pages_processed = 0
        for processor_instance in self.processor_instances.all():
            novel_link_pages_processed += processor_instance.novel_link_pages_processed
            chapter_link_pages_processed += (
                processor_instance.chapter_link_pages_processed
            )
            novel_pages_processed += processor_instance.novel_pages_processed
            chapter_pages_processed += processor_instance.chapter_pages_processed
        return (
            novel_link_pages_processed,
            chapter_link_pages_processed,
            novel_pages_processed,
            chapter_pages_processed,
        )


class UpdateSpiderInstance(models.Model):
    novel_link_pages_scraped = models.IntegerField(default=0)
    chapter_link_pages_scraped = models.IntegerField(default=0)
    novel_pages_scraped = models.IntegerField(default=0)
    chapter_pages_scraped = models.IntegerField(default=0)

    t_start = models.DateTimeField(auto_now=True)
    update_process_instance = models.ForeignKey(
        UpdateProcessInstance, on_delete=models.CASCADE, related_name="spider_instances"
    )


class UpdateProcessorInstance(models.Model):
    novel_link_pages_processed = models.IntegerField(default=0)
    chapter_link_pages_processed = models.IntegerField(default=0)
    novel_pages_processed = models.IntegerField(default=0)
    chapter_pages_processed = models.IntegerField(default=0)

    t_start = models.DateTimeField(auto_now=True)
    update_process_instance = models.ForeignKey(
        UpdateProcessInstance,
        on_delete=models.CASCADE,
        related_name="processor_instances",
    )
