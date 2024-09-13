import links_manager.models as lm_models
from spiders_manager.models import get_novel_page
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("max_allowed_processes_per_site", nargs="+", type=int)

    def handle(self, *args, **options):
        pass
