import spiders_manager.models as sm_models
import novels_storage.models as ns_models
import os
from django.core.management.base import BaseCommand
from time import sleep

WEBSITE_UPDATE_CYCLE_REFRESH_TIME = 0.5
NOVEL_UPDATE_CYCLE_REFRESH_TIME = 0.1


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("website_name", type=str)

    def handle(self, website_name, *args, **options):
        website = ns_models.Website.objects.get(name=website_name)
        while True:
            website_update_instance = sm_models.WebsiteUpdateInstance.objects.get(
                website=website
            )
            os.system("clear")
            print(website_update_instance)
            sleep(1)
