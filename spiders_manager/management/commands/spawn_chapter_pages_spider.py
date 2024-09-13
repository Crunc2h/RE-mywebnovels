import links_manager.models as lm_models
from spiders_manager.models import get_chapter_pages
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("novel_link", nargs="+", type=str)

    def handle(self, *args, **options):
        novel_link_object = lm_models.NovelLink.objects.get(
            link=options["novel_link"][0]
        )
        get_chapter_pages(
            chapter_pages_directory=novel_link_object.chapter_pages_directory,
            chapter_urls=novel_link_object.get_uninitialized_chapter_links(),
        )
