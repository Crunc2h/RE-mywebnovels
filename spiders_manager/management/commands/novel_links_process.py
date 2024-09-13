from spiders_manager.models import get_novel_links
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("crawler_start_link", nargs="+", type=str)
        parser.add_argument("novel_link_pages_dir", nargs="+", type=str)

    def handle(self, *args, **options):
        get_novel_links(
            novel_link_pages_dir=options["novel_link_pages_dir"][0],
            crawler_start_link=options["crawler_start_link"][0],
        )
