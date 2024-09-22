import subprocess
import time
import proxy_manager.models as pm_models
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        pm_models.Proxy.objects.all().delete()
        while True:
            subprocess.run("python3 manage.py proxy_fetcher", shell=True)
