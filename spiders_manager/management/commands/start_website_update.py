import subprocess
import links_manager.models as lm_models
import novels_storage.models as ns_models
from django.core.management.base import BaseCommand

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

        novel_link_pages_process = subprocess.run(
            f"python3 manage.py open_novel_link_pages_process '{website.name}'",
            shell=True,
        )

        novel_link_objects_present = website.link_object.novel_links.all()
        [print(n.link) for n in novel_link_objects_present]

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
        """
        urls = [
            "https://www.webnovelpub.pro/novel/a-depressed-kendo-player-possesses-a-bastard-aristocrat",
            "https://www.webnovelpub.pro/novel/i-became-the-necromancer-of-the-academy",
        ]

        from spiders_manager.native.website_abstraction.website_interface import (
            WebsiteInterface,
        )

        test_wi = WebsiteInterface(website.name, caller="urmom")
        for url in urls:
            a = lm_models.NovelLink(
                name=test_wi.get_novel_name_from_url(url),
                link=url,
                website_link=website.link_object,
            )
            a.save()
        novel_page_url_batches = [
            [
                "https://www.webnovelpub.pro/novel/a-depressed-kendo-player-possesses-a-bastard-aristocrat",
                "https://www.webnovelpub.pro/novel/i-became-the-necromancer-of-the-academy",
            ]
        ]
        """
        procs = []
        for batch in novel_page_url_batches:
            args = [
                "python3",
                "manage.py",
                "open_novel_pages_process",
                f"{website.name}",
            ]
            for url in batch:
                args.append(url)
            print(args)
            procs.append(subprocess.Popen(args=args))

        for novel_pages_process in procs:
            novel_pages_process.wait()
