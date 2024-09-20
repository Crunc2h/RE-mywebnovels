import os
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import models
from datetime import datetime, timezone
from cout.native.common import standardize_str


class NovelAuthor(models.Model):
    name = models.CharField(max_length=512)


class NovelLanguage(models.Model):
    name = models.CharField(max_length=512)


class NovelCompletionStatus(models.Model):
    name = models.CharField(max_length=512)


class NovelCategory(models.Model):
    name = models.CharField(max_length=512)


class NovelTag(models.Model):
    name = models.CharField(max_length=512)


def get_or_create_enum_model_from_str(enum_str, enum_type):
    enum_str = standardize_str(enum_str)
    try:
        matching_enum = enum_type.objects.get(name=enum_str)
        return matching_enum
    except ObjectDoesNotExist:
        new_enum = enum_type(name=enum_str)
        new_enum.save()
        return new_enum
    except MultipleObjectsReturned as ex:
        raise ex


WEBSITES_DIR_NAME = "websites"
NOVEL_LINK_PAGES_DIR_NAME = "novel_link_pages"
NOVEL_PAGES_DIR_NAME = "novel_pages"
NOVELS_DIR_NAME = "novels"
CHAPTER_LINK_PAGES_DIR_NAME = "chapter_link_pages"
CHAPTER_PAGES_DIR_NAME = "chapter_pages"
NOVEL_UPDATE_THRESHOLD_MINUTES = 720


class Website(models.Model):
    name = models.CharField(max_length=128)
    website_directory = models.CharField(max_length=2048, blank=True, null=True)
    novel_link_pages_directory = models.CharField(
        max_length=8096, blank=True, null=True
    )
    novels_directory = models.CharField(max_length=2048, blank=True, null=True)

    def save(self):
        self.name = standardize_str(self.name)

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

    def get_novel_of_name(self, novel_name):
        novel_name = standardize_str(novel_name)
        matching_novels = self.novels.filter(name=novel_name)
        if matching_novels.exists():
            return matching_novels.first()
        return None


class Novel(models.Model):
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE, related_name="novels"
    )
    name = models.CharField(max_length=512)
    summary = models.TextField(max_length=16256, blank=True, null=True)
    author = models.ForeignKey(
        NovelAuthor,
        on_delete=models.CASCADE,
        related_name="novels",
        blank=True,
        null=True,
    )
    language = models.ForeignKey(
        NovelLanguage,
        on_delete=models.CASCADE,
        related_name="novels",
        blank=True,
        null=True,
    )
    completion_status = models.ForeignKey(
        NovelCompletionStatus,
        on_delete=models.CASCADE,
        related_name="novels",
        blank=True,
        null=True,
    )
    categories = models.ManyToManyField(NovelCategory, related_name="novels")
    tags = models.ManyToManyField(NovelTag, related_name="novels")
    novel_directory = models.CharField(max_length=2048, blank=True, null=True)
    chapter_link_pages_directory = models.CharField(
        max_length=2048, blank=True, null=True
    )
    chapter_pages_directory = models.CharField(max_length=2048, blank=True, null=True)
    novel_directory = models.CharField(max_length=2048, blank=True, null=True)
    chapter_link_pages_directory = models.CharField(
        max_length=2048, blank=True, null=True
    )
    chapter_pages_directory = models.CharField(max_length=2048, blank=True, null=True)
    initialized = models.BooleanField(default=False)
    is_being_updated = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Novel --> {self.name}\n\
Author: {self.author.name}\n\
Completion Status: {self.completion_status.name}\n\
Initialized: {self.initialized}\n\
Is Being Updated: {self.is_being_updated}\n\
Link: {'None' if not hasattr(self, 'link') else self.link}\n\
Chapters: {self.chapters.count()}\n\
Categories --> {[category.name for category in self.categories.all()]}\n\
Tags --> {[tag.name for tag in self.tags.all()]}"

    def save(self) -> None:
        self.name = standardize_str(self.name)

        self.novel_directory = (
            self.website.novels_directory
            + "/"
            + "".join([letter for letter in self.name if letter != " "])
        )
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

        return super().save()

    def is_updatable(self):
        if self.is_being_updated:
            return False
        if not self.initialized or self.chapters.count() == 0:
            return True
        return (
            datetime.now(timezone.utc) - self.last_updated
        ).seconds // 60 >= NOVEL_UPDATE_THRESHOLD_MINUTES

    def get_chapter_of_name(self, chapter_name):
        chapter_name = standardize_str(chapter_name)
        matching_chapters = self.chapters.filter(name=chapter_name)
        if matching_chapters.exists():
            return matching_chapters.first()
        return None


class Chapter(models.Model):
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name="chapters")
    date_published = models.DateField()
    name = models.CharField(max_length=512)
    number = models.CharField(max_length=128)
    text = models.TextField(max_length=32512)

    def save(self) -> None:
        self.name = standardize_str(self.name)
        self.number = standardize_str(self.number)
        return super().save()


def dbwide_get_novel_of_name(novel_name):
    novel_name = standardize_str(novel_name)
    matching_novels = Novel.objects.filter(name=novel_name)
    if len(matching_novels) > 0:
        return matching_novels.first()
    return None


def bulk_dbwide_get_novels_of_name_by_nldicts(new_novel_link_object_dicts):
    all = Novel.objects.all()
    novel_names = [novel.name for novel in all]
    existing_links = []
    new_links = []
    for novel_link_object_dict in new_novel_link_object_dicts:
        if novel_link_object_dict["name"] in novel_names:
            existing_links.append(novel_link_object_dict)
        else:
            new_links.append(novel_link_object_dict)
    matching_novels_and_dicts = [
        (all.get(name=novel_link_object_dict["name"]), novel_link_object_dict)
        for novel_link_object_dict in existing_links
    ]
    return matching_novels_and_dicts, new_links
