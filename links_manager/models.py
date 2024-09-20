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
        return novel_link in [
            novel_link_object.link
            for novel_link_object in self.novel_link_objects.all()
        ]

    def bulk_get_absent_novel_links(self, new_novel_link_object_dicts):
        present_links = [
            novel_link_object.link
            for novel_link_object in self.novel_link_objects.all()
        ]
        absent_links = []
        for novel_object_dict in new_novel_link_object_dicts:
            if novel_object_dict["link"] not in present_links:
                absent_links.append(novel_object_dict)
        return absent_links

    def get_novel_link_object_from_url(self, novel_link):
        if self.novel_links.filter(link=novel_link).count() > 0:
            return self.novel_links_objects.get(link=novel_link)
        return None


class NovelLink(models.Model):
    website_link_object = models.ForeignKey(
        WebsiteLink, on_delete=models.CASCADE, related_name="novel_link_objects"
    )
    novel = models.OneToOneField(
        ns_models.Novel,
        on_delete=models.CASCADE,
        related_name="link_object",
    )
    link = models.CharField(max_length=8096)
    name = models.CharField(max_length=1024)

    def chapter_link_exists(self, chapter_link):
        return chapter_link in [
            chapter_link.link for chapter_link in self.chapter_link_objects.all()
        ]


class ChapterLink(models.Model):
    novel_link_object = models.ForeignKey(
        NovelLink,
        on_delete=models.CASCADE,
        related_name="chapter_link_objects",
    )
    link = models.CharField(max_length=8096)
    name = models.CharField(max_length=1024)
