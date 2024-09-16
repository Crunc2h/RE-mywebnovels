import novels_storage.models as ns_models
from django.db import models


class UpdateCycle(models.Model):
    maximum_processes_per_site = models.IntegerField()
    t_start = models.DateTimeField(auto_now=True)

    db_processes_idle = models.IntegerField(default=0)
    db_processes_in_progress = models.IntegerField(default=0)
    db_processes_scraper_error = models.IntegerField(default=0)
    db_processes_processor_error = models.IntegerField(default=0)
    db_processes_launch_error = models.IntegerField(default=0)
    db_processes_finished = models.IntegerField(default=0)

    db_novel_links = models.IntegerField(default=0)
    db_chapter_links = models.IntegerField(default=0)
    db_novels = models.IntegerField(default=0)
    db_chapters = models.IntegerField(default=0)
    db_unmatched_novel_links = models.IntegerField(default=0)
    db_existing_novels_updated = models.IntegerField(default=0)

    db_new_novel_links_added = models.IntegerField(default=0)
    db_new_chapter_links_added = models.IntegerField(default=0)
    db_new_novels_added = models.IntegerField(default=0)
    db_new_chapters_added = models.IntegerField(default=0)


class WebsiteUpdateInstance(models.Model):
    maximum_processes = models.IntegerField()
    update_cycle = models.ForeignKey(
        UpdateCycle, on_delete=models.CASCADE, related_name="website_update_instances"
    )
    website = models.OneToOneField(
        ns_models.Website, on_delete=models.CASCADE, related_name="update_instance"
    )
    t_start = models.DateTimeField(auto_now=True)
    critical_error = models.BooleanField(default=False)
    critical_error_message = models.CharField(max_length=4096, blank=True, null=True)

    site_processes_idle = models.IntegerField(default=0)
    site_processes_in_progress = models.IntegerField(default=0)
    site_processes_scraper_error = models.IntegerField(default=0)
    site_processes_processor_error = models.IntegerField(default=0)
    site_processes_launch_error = models.IntegerField(default=0)
    site_processes_finished = models.IntegerField(default=0)

    site_novel_links = models.IntegerField(default=0)
    site_chapter_links = models.IntegerField(default=0)
    site_novels = models.IntegerField(default=0)
    site_chapters = models.IntegerField(default=0)
    site_unmatched_novel_links = models.IntegerField(default=0)
    site_existing_novels_updated = models.IntegerField(default=0)
    site_unmatched_novel_links = models.IntegerField(default=0)

    site_new_novel_links_added = models.IntegerField(default=0)
    site_new_chapter_links_added = models.IntegerField(default=0)
    site_new_novels_added = models.IntegerField(default=0)
    site_new_chapters_added = models.IntegerField(default=0)


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
    maximum_scraper_grace_period = models.IntegerField(default=1)
    current_scraper_grace_period = models.IntegerField(default=0)
    max_processor_retry_on_bad_content = models.IntegerField(default=5)
    current_processor_retry_on_bad_content = models.IntegerField(default=0)
    bad_content_page_paths = models.CharField(max_length=32128, blank=True, null=True)
    exception_message = models.CharField(max_length=4096, blank=True, null=True)
