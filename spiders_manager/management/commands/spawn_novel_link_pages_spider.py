import links_manager.models as lm_models
from spiders_manager.models import get_novel_links
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("website_name", nargs="+", type=str)

    def handle(self, *args, **options):
        website_object = lm_models.Website.objects.get(name=options["website_name"][0])

        get_novel_links(
            novel_link_pages_dir=website_object.novel_link_pages_directory,
            crawler_start_link=website_object.crawler_start_link,
        )
