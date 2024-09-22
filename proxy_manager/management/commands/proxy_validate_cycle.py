import subprocess
import time
import proxy_manager.models as pm_models
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        while True:
            if pm_models.Proxy.objects.count() == 0:
                time.sleep(20)
            subprocess.run("python3 manage.py proxy_validator", shell=True)
