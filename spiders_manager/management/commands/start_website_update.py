import subprocess
import os
import spiders_manager.models as sm_models
import links_manager.models as lm_models
import novels_storage.models as ns_models
from django.core.management.base import BaseCommand
from time import sleep

WEBSITE_UPDATE_CYCLE_REFRESH_TIME = 0.5
NOVEL_UPDATE_CYCLE_REFRESH_TIME = 0.1


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("website_name", nargs="+", type=str)
        parser.add_argument("max_allowed_processes", nargs="+", type=int)

    def handle(self, *args, **options):
        lm_models.NovelLink.objects.all().delete()
        lm_models.ChapterLink.objects.all().delete()
        ns_models.Website.objects.all().delete()
        ns_models.Chapter.objects.all().delete()
        ns_models.Novel.objects.all().delete()
        sm_models.WebsiteUpdateInstance.objects.all().delete()
        sm_models.UpdateProcessInstance.objects.all().delete()
        sm_models.UpdateProcessorInstance.objects.all().delete()
        sm_models.UpdateSpiderInstance.objects.all().delete()

        website = ns_models.Website(
            name="webnovelpub",
        )
        website.save()

        website_link_object = lm_models.WebsiteLink(
            website=website,
            base_link="https://www.webnovelworld.org",
            crawler_start_link="https://www.webnovelpub.pro/browse/genre-all-25060123/order-new/status-all",
        )
        website_link_object.save()

        website_update_instance = sm_models.WebsiteUpdateInstance(website=website)
        website_update_instance.save()

        os.system(
            "gnome-terminal -- "
            + f"bash -c 'source .re_venv/bin/activate; python3 manage.py website_update_display '{website.name}'; exec bash;'"
        )

        new_update_process_instance = sm_models.UpdateProcessInstance(
            process_id=0, website_update_instance=website_update_instance
        )
        new_update_process_instance.save()
        novel_link_pages_process = subprocess.run(
            f"python3 manage.py open_novel_link_pages_process 0 '{website.name}'",
            shell=True,
            check=True,
        )

        novel_link_objects_present = list(website.link_object.novel_links.all())

        max_processes = options["max_allowed_processes"][0]
        novel_page_url_batches = []
        novel_page_url_per_batch = len(novel_link_objects_present) // max_processes
        last_step = 0
        for i in range(0, max_processes):
            if i != max_processes - 1:
                novel_page_url_batches.append(
                    [
                        novel_link_object.link
                        for novel_link_object in novel_link_objects_present[
                            last_step : last_step + novel_page_url_per_batch
                        ]
                    ]
                )
                last_step += novel_page_url_per_batch
            else:
                novel_page_url_batches.append(
                    [
                        novel_link_object.link
                        for novel_link_object in novel_link_objects_present[last_step::]
                    ]
                )

        novel_page_processes = []
        for i in range(len(novel_page_url_batches)):
            new_update_process_instance = sm_models.UpdateProcessInstance(
                process_id=i + 1, website_update_instance=website_update_instance
            )
            new_update_process_instance.save()

            args = [
                "python3",
                "manage.py",
                "open_novel_pages_process",
                f"{i + 1}",
                f"{website.name}",
            ]
            args.extend(novel_page_url_batches[i])
            novel_page_processes.append(subprocess.Popen(args=args))

        for novel_pages_process in novel_page_processes:
            novel_pages_process.wait()
