import os
from datetime import datetime, timezone
from django.db import models
from django.db.models import Q

WEBSITES_DIR_NAME = "websites"
NOVEL_LINK_PAGES_DIR_NAME = "novel_link_pages"
NOVEL_PAGES_DIR_NAME = "novel_pages"
NOVELS_DIR_NAME = "novels"
CHAPTER_LINK_PAGES_DIR_NAME = "chapter_link_pages"
CHAPTER_PAGES_DIR_NAME = "chapter_pages"
NOVEL_UPDATE_THRESHOLD_MINUTES = 720


class Website(models.Model):
    name = models.CharField(max_length=128)
    link = models.CharField(max_length=8096)
    crawler_start_link = models.CharField(max_length=8096)
    website_directory = models.CharField(max_length=2048, blank=True, null=True)
    novel_link_pages_directory = models.CharField(
        max_length=8096, blank=True, null=True
    )
    novels_directory = models.CharField(max_length=2048, blank=True, null=True)

    def save(self):
        self.website_directory = (
            os.path.dirname(os.path.realpath(__file__)) + "/"
            "websites" + "/" + self.name
        )
        if not os.path.exists(self.website_directory):
            os.makedirs(self.website_directory)

        self.novel_link_pages_directory = (
            self.website_directory + "/" + NOVEL_LINK_PAGES_DIR_NAME
        )
        if not os.path.exists(self.novel_link_pages_directory):
            os.makedirs(self.novel_link_pages_directory)

        self.novels_directory = self.website_directory + "/" + "novels"
        if not os.path.exists(self.novels_directory):
            os.makedirs(self.novels_directory)

        return super().save()

    def novel_link_exists(self, novel_link):
        return novel_link in [novel_link.link for novel_link in self.novel_links.all()]

    def novel_exists_normal_name(self, novel_normal_name):
        existing_novels = [
            novel_link.novel.name
            for novel_link in self.novel_links.all()
            if novel_link.initialized
        ]
        return novel_normal_name.lower() in existing_novels

    def novel_exists_slug_name(self, novel_slug_name):
        existing_novels = [
            novel_link.slug_name for novel_link in self.novel_links.all()
        ]
        return novel_slug_name.lower() in existing_novels


class NovelLink(models.Model):
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE, related_name="novel_links"
    )
    slug_name = models.CharField(max_length=1024)
    link = models.CharField(max_length=8096)
    initialized = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    novel_directory = models.CharField(max_length=2048, blank=True, null=True)
    chapter_link_pages_directory = models.CharField(
        max_length=2048, blank=True, null=True
    )
    chapter_pages_directory = models.CharField(max_length=2048, blank=True, null=True)

    def save(self):
        self.novel_directory = self.website.novels_directory + "/" + self.slug_name
        if not os.path.exists(self.novel_directory):
            os.makedirs(self.novel_directory)

        self.chapter_link_pages_directory = (
            self.novel_directory + "/" + CHAPTER_LINK_PAGES_DIR_NAME
        )
        if not os.path.exists(self.chapter_link_pages_directory):
            os.makedirs(self.chapter_link_pages_directory)

        self.chapter_pages_directory = (
            self.novel_directory + "/" + CHAPTER_PAGES_DIR_NAME
        )
        if not os.path.exists(self.chapter_pages_directory):
            os.makedirs(self.chapter_pages_directory)

        self.slug_name = self.slug_name.lower()

        return super().save()

    def chapter_link_exists(self, chapter_link):
        return chapter_link in [
            chapter_link.link for chapter_link in self.chapter_links.all()
        ]

    def get_uninitialized_chapter_links(self):
        return [
            chapter_link.link
            for chapter_link in self.chapter_links.filter(initialized=False).all()
        ]

    def is_updatable(self):
        if not self.initialized:
            return True
        return (
            datetime.now(timezone.utc) - self.last_updated
        ).seconds // 60 >= NOVEL_UPDATE_THRESHOLD_MINUTES

    def get_normal_name(self):
        return " ".join([word.lower() for word in self.slug_name.split("-")])


class ChapterLink(models.Model):
    novel_link = models.ForeignKey(
        NovelLink, on_delete=models.CASCADE, related_name="chapter_links"
    )
    initialized = models.BooleanField(default=False)
    link = models.CharField(max_length=8096)
    name = models.CharField(max_length=1024)


def db_novel_exists(novel_normal_name):
    for website in Website.objects.all():
        if website.novel_exists_normal_name(novel_normal_name):
            return True
    return False
