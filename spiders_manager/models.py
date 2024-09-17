import novels_storage.models as ns_models
import spiders_manager.native.website_abstraction.process_signals as signals
from django.db import models
from django.dispatch import receiver


class UpdateCycle(models.Model):
    maximum_processes_per_site = models.IntegerField()
    t_start = models.DateTimeField(auto_now=True)

    processes_idle = models.IntegerField(default=0)
    processes_in_progress = models.IntegerField(default=0)
    processes_bad_content = models.IntegerField(default=0)
    processes_error = models.IntegerField(default=0)
    processes_complete = models.IntegerField(default=0)

    novel_link_pages_scraped = models.IntegerField(default=0)
    novel_pages_scraped = models.IntegerField(default=0)
    chapter_link_pages_scraped = models.IntegerField(default=0)
    chapter_pages_scraped = models.IntegerField(default=0)

    novel_link_pages_processed = models.IntegerField(default=0)
    novel_pages_processed = models.IntegerField(default=0)
    chapter_link_pages_processed = models.IntegerField(default=0)
    chapter_pages_processed = models.IntegerField(default=0)

    novel_links_present = models.IntegerField(default=0)
    novels_present = models.IntegerField(default=0)
    chapter_links_present = models.IntegerField(default=0)
    chapters_present = models.IntegerField(default=0)

    new_novels_added = models.IntegerField(default=0)
    new_chapters_added = models.IntegerField(default=0)


class WebsiteUpdateInstance(models.Model):
    maximum_processes = models.IntegerField()
    update_cycle = models.ForeignKey(
        UpdateCycle, on_delete=models.CASCADE, related_name="website_update_instances"
    )
    website = models.OneToOneField(
        ns_models.Website, on_delete=models.CASCADE, related_name="update_instance"
    )
    t_start = models.DateTimeField(auto_now=True)

    critical_errors_faced = models.IntegerField(default=0)
    scraper_errors_faced = models.IntegerField(default=0)
    bad_content_errors_faced = models.IntegerField(default=0)

    novel_links_found = models.IntegerField(default=0)
    chapter_links_found = models.IntegerField(default=0)

    novels_present = models.IntegerField(default=0)
    chapters_present = models.IntegerField(default=0)

    new_novels_added = models.IntegerField(default=0)
    new_chapters_added = models.IntegerField(default=0)

    novel_link_pages_scraped = models.IntegerField(default=0)
    novel_pages_scraped = models.IntegerField(default=0)
    chapter_link_pages_scraped = models.IntegerField(default=0)
    chapter_pages_scraped = models.IntegerField(default=0)

    novel_link_pages_processed = models.IntegerField(default=0)
    novel_pages_processed = models.IntegerField(default=0)
    chapter_link_pages_processed = models.IntegerField(default=0)
    chapter_pages_processed = models.IntegerField(default=0)

    novels_update_left = models.IntegerField(default=0)
    novels_updated_per_min = models.FloatField(default=0)
    novels_updated = models.IntegerField(default=0)
    sum_novel_process_times = models.IntegerField(default=0)

    def __str__(self) -> str:
        processes = "\n" + "\n".join(
            [f"PROCESSxx: {process.state}" for process in self.spider_processes.all()]
        )
        body = f"\n\
({self.novels_updated_per_min} novels per min avg.) \n\
novels updated: {self.novels_updated}\n\
\n\
critical errors faced: {self.critical_errors_faced}\n\
scraper_errors_faced: {self.scraper_errors_faced}\n\
bad_content_errors_faced: {self.bad_content_errors_faced}\n\
\n\
novel link pages scraped: {self.novel_link_pages_scraped}\n\
novel pages scraped: {self.novel_pages_scraped}\n\
chapter link pages scraped: {self.chapter_link_pages_scraped}\n\
chapter pages scraped: {self.chapter_pages_scraped}\n\
\n\
novel link pages processed: {self.novel_link_pages_processed}\n\
novel pages processed: {self.novel_pages_processed}\n\
chapter link pages processed: {self.chapter_link_pages_processed}\n\
chapter pages processed: {self.chapter_pages_processed}\n\
\n\
novel links found: {self.novel_links_found}\n\
chapter links found: {self.chapter_links_found}\n\
novels present: {self.website.novels.count()}\n\
chapters present: {sum([novel.chapters.count() for novel in self.website.novels.all()])}"
        return body + processes

    @receiver(signals.novel_link_page_scraped)
    def scrape__novel_link_page(sender, **kwargs):
        instance = kwargs.get("instance")
        instance.novel_link_pages_scraped += 1
        instance.save()

    @receiver(signals.novel_page_scraped)
    def scrape__novel_page(sender, **kwargs):
        instance = kwargs.get("instance")
        instance.novel_pages_scraped += 1
        instance.save()

    @receiver(signals.chapter_link_page_scraped)
    def scrape__chapter_link_page(sender, **kwargs):
        instance = kwargs.get("instance")
        instance.chapter_link_pages_scraped += 1
        instance.save()

    @receiver(signals.chapter_page_scraped)
    def scrape__chapter_page(sender, **kwargs):
        instance = kwargs.get("instance")
        instance.chapter_pages_scraped += 1
        instance.save()

    @receiver(signals.novel_link_page_processed)
    def process__novel_link_page(sender, **kwargs):
        instance = kwargs.get("instance")
        instance.novel_link_pages_processed += 1
        instance.save()

    @receiver(signals.novel_page_processed)
    def process__novel_page(sender, **kwargs):
        instance = kwargs.get("instance")
        instance.novel_pages_processed += 1
        instance.save()

    @receiver(signals.chapter_link_page_processed)
    def process__chapter_link_page(sender, **kwargs):
        instance = kwargs.get("instance")
        instance.chapter_link_pages_processed += 1
        instance.save()

    @receiver(signals.chapter_page_processed)
    def process__chapter_page(sender, **kwargs):
        instance = kwargs.get("instance")
        instance.chapter_pages_processed += 1
        instance.save()

    @receiver(signals.process_finish)
    def process__finish(sender, **kwargs):
        instance = kwargs.get("instance")
        process_time = kwargs.get("time")
        instance.sum_novel_process_times += process_time
        instance.novels_updated += 1
        novel_update_speed_avg = (
            instance.sum_novel_process_times / instance.novels_updated
        )
        instance.novels_updated_per_min = 60 / novel_update_speed_avg
        instance.novels_update_left = len(
            [novel for novel in instance.website.novels.all() if novel.is_updatable()]
        )
        instance.save()

    @receiver(signals.new_novel_links_added)
    def add__novel_link(sender, **kwargs):
        instance = kwargs.get("instance")
        instance.novel_links_found += 1
        instance.save()

    @receiver(signals.new_chapter_links_added)
    def add__chapter_link(sender, **kwargs):
        instance = kwargs.get("instance")
        instance.chapter_links_found += 1
        instance.save()

    @receiver(signals.new_novels_added)
    def add__new_novel(sender, **kwargs):
        instance = kwargs.get("instance")
        instance.new_novels_added += 1
        instance.save()

    @receiver(signals.new_chapters_added)
    def add__new_chapter(sender, **kwargs):
        instance = kwargs.get("instance")
        instance.new_chapters_added += 1
        instance.save()

    @receiver(signals.scraper_error)
    def error_scraper(sender, **kwargs):
        instance = kwargs.get("instance")
        instance.scraper_errors_faced += 1
        instance.save()

    @receiver(signals.bad_content_error)
    def error_bad_content(sender, **kwargs):
        instance = kwargs.get("instance")
        instance.bad_content_errors_faced += 1
        instance.save()

    @receiver(signals.critical_error)
    def error__critical(sender, **kwargs):
        instance = kwargs.get("instance")
        instance.critical_errors_faced += 1
        instance.save()


class SpiderInstanceProcessState:
    SCRAPER_ERROR = "scraper_error"
    PROCESSOR_ERROR = "processor_error"
    IDLE = "idle"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    COMPLETE = "complete"
    BAD_CONTENT = "bad_content"


class SpiderInstanceProcess(models.Model):
    website_update_instance = models.ForeignKey(
        WebsiteUpdateInstance, on_delete=models.CASCADE, related_name="spider_processes"
    )
    identifier = models.CharField(max_length=8096)
    state = models.CharField(max_length=64, default=SpiderInstanceProcessState.IDLE)
    maximum_scraper_grace_period = models.IntegerField(default=5)
    current_scraper_grace_period = models.IntegerField(default=0)
    max_processor_retry_on_bad_content = models.IntegerField(default=5)
    current_processor_retry_on_bad_content = models.IntegerField(default=0)
    bad_content_page_paths = models.CharField(max_length=32128, blank=True, null=True)
    exception_message = models.CharField(max_length=4096, blank=True, null=True)
