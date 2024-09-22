import scrapy
import cout.native.console as cout
import spiders_manager.models as sm_models
import novels_storage.models as ns_models
from typing import Iterable
from pathlib import Path
from proxy_manager.models import modify_with_proxy
from fake_useragent import UserAgent


FILE_FORMAT = "html"
NOVEL_PAGE_FORMAT = "/novel_page.{file_format}"


class NovelPagesSpider(scrapy.Spider):
    name = "novel_pages_spider"
    start_urls = []
    user_agent_fetcher = UserAgent(browsers="firefox")
    download_delay = 0.5

    def __init__(
        self,
        process_id,
        website_name,
        novel_page_urls_to_novel_directories,
        *args,
        **kwargs,
    ):
        self.process_id = process_id
        self.website_name = website_name

        self.update_process_instance = ns_models.Website.objects.get(
            name=self.website_name
        ).update_instance.process_instances.get(process_id=self.process_id)

        self.spider_instance = sm_models.UpdateSpiderInstance(
            update_process_instance=self.update_process_instance
        )
        self.spider_instance.save()

        self.novel_page_urls_to_novel_directories = novel_page_urls_to_novel_directories
        self.start_urls.extend(list(self.novel_page_urls_to_novel_directories.keys()))

        self.cout = cout.ConsoleOut(header="SC_BOTS::NOVEL_PAGES_SPIDER")
        super().__init__(*args, **kwargs)
        self.cout.broadcast(style="success", message="Successfully initialized.")

    def start_requests(self) -> Iterable[scrapy.Request]:
        super().start_requests()
        for url in self.start_urls:
            yield modify_with_proxy(
                scrapy.Request(
                    url,
                    self.parse,
                    dont_filter=True,
                    headers={"User-Agent": self.user_agent_fetcher.random},
                )
            )

    def parse(self, response):
        current_novel_directory = self.novel_page_urls_to_novel_directories[
            response.url
        ]
        self.cout.broadcast(
            style="progress",
            message=f"<{response.status}> Crawling {response.url}...",
        )
        Path(
            current_novel_directory + NOVEL_PAGE_FORMAT.format(file_format=FILE_FORMAT)
        ).write_bytes(response.body)

        self.spider_instance.novel_pages_scraped += 1
        self.spider_instance.save()
