from typing import Iterable
import links_manager.models as lm_models
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import models

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
    enum_str = enum_str.lower()
    try:
        matching_enum = enum_type.objects.get(name=enum_str)
        return matching_enum
    except ObjectDoesNotExist:
        new_enum = enum_type(name=enum_str)
        new_enum.save()
        return new_enum
    except MultipleObjectsReturned as ex:
        raise ex



class Novel(models.Model):
    name = models.CharField(max_length=512)
    summary = models.TextField(max_length=16256)
    number_of_chapters = models.IntegerField()
    
    link = models.OneToOneField(lm_models.NovelLink, on_delete=models.PROTECT, related_name="novel")
    author = models.ForeignKey(NovelAuthor, on_delete=models.PROTECT, related_name="novels")
    language = models.ForeignKey(NovelLanguage, on_delete=models.PROTECT, related_name="novels")
    completion_status = models.ForeignKey(NovelCompletionStatus, on_delete=models.PROTECT, related_name="novels")
    categories = models.ManyToManyField(NovelCategory, related_name="novels")
    tags = models.ManyToManyField(NovelTag, related_name="novels")

    def save(self) -> None:
        self.name = self.name.lower()
        return super().save()

class Chapter(models.Model):
    link = models.OneToOneField(lm_models.ChapterLink, on_delete=models.PROTECT, related_name="chapter")
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name="chapters")
    
    date_uploaded = models.DateField()
    name = models.CharField(max_length=512)
    text = models.TextField(max_length=32512)

    def save(self) -> None:
        self.name = self.name.lower()
        return super().save()
