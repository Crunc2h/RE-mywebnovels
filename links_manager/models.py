import os
import novels_storage.models as ns_models
from datetime import datetime, timezone
from django.db import models
from django.db.models import Q


class WebsiteLink(models.Model):
    website = models.OneToOneField(
        ns_models.Website, on_delete=models.CASCADE, related_name="link_object"
    )
    base_link = models.CharField(max_length=8096)
    crawler_start_link = models.CharField(max_length=8096)

    def novel_link_exists(self, novel_link):
        return novel_link in [novel_link.link for novel_link in self.novel_links.all()]

    def get_novel_link_object_from_url(self, novel_link):
        if self.novel_links.filter(link=novel_link).count() > 0:
            return self.novel_links.get(link=novel_link)
        return None


class NovelLink(models.Model):
    website_link = models.ForeignKey(
        WebsiteLink, on_delete=models.CASCADE, related_name="novel_links"
    )
    novel = models.OneToOneField(
        ns_models.Novel,
        on_delete=models.CASCADE,
        related_name="link",
        blank=True,
        null=True,
    )
    link = models.CharField(max_length=8096)
    name = models.CharField(max_length=1024)

    def chapter_link_exists(self, chapter_link):
        return chapter_link in [
            chapter_link.link for chapter_link in self.chapter_links.all()
        ]


class ChapterLink(models.Model):
    novel_link = models.ForeignKey(
        NovelLink,
        on_delete=models.CASCADE,
        related_name="chapter_links",
    )
    link = models.CharField(max_length=8096)
    name = models.CharField(max_length=1024)
