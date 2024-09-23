import scrapy
import spiders_manager.models as sm_models
import novels_storage.models as ns_models
import cout.native.console as cout
from pathlib import Path
from proxy_manager.models import modify_with_proxy, proxy_exists
from twisted.internet.error import TimeoutError
from scrapy.spidermiddlewares.httperror import HttpError
from fake_useragent import UserAgent


FILE_FORMAT = "html"
CHAPTER_PAGES_FORMAT = "/chapter-{current_chapter}.{file_format}"


class ChapterPagesSpider(scrapy.Spider):
    name = "chapter_pages_spider"
    start_urls = []
    user_agent_fetcher = UserAgent(browsers="firefox")
    chapter_page_numbers_used = []
    download_delay = 0.5

    def __init__(
        self,
        process_id,
        website_name,
        chapter_urls_to_chapter_page_directories,
        use_proxy=False,
        *args,
        **kwargs,
    ):
        self.process_id = process_id
        self.website_name = website_name
        self.use_proxy = use_proxy

        self.update_process_instance = ns_models.Website.objects.get(
            name=self.website_name
        ).update_instance.process_instances.get(process_id=self.process_id)
        self.spider_instance = sm_models.UpdateSpiderInstance(
            update_process_instance=self.update_process_instance
        )
        self.spider_instance.save()

        self.chapter_urls_to_chapter_page_directories = (
            chapter_urls_to_chapter_page_directories
        )
        self.start_urls.extend(list(chapter_urls_to_chapter_page_directories.keys()))
        self.cout = cout.ConsoleOut(header="SC_BOTS::CHAPTER_PAGES_SPIDER")
        super().__init__(*args, **kwargs)
        self.cout.broadcast(style="success", message="Successfully initialized.")

    def start_requests(self):
        super().start_requests()
        for url in self.start_urls:
            if self.use_proxy:
                request = scrapy.Request(
                    url,
                    self.parse,
                    dont_filter=True,
                    headers={"User-Agent": self.user_agent_fetcher.random},
                )
                modified = modify_with_proxy(request)
                yield modified
            else:
                yield scrapy.Request(
                    url,
                    self.parse,
                    dont_filter=True,
                    headers={"User-Agent": self.user_agent_fetcher.random},
                )

    def parse(self, response):
        current_chapter_pages_directory = self.chapter_urls_to_chapter_page_directories[
            response.url
        ]
        self.cout.broadcast(
            style="progress",
            message=f"<{response.status}> Crawling {response.url}...",
        )

        Path(
            current_chapter_pages_directory
            + CHAPTER_PAGES_FORMAT.format(
                current_chapter=self.spider_instance.chapter_link_pages_scraped,
                file_format=FILE_FORMAT,
            )
        ).write_bytes(response.body)

        self.spider_instance.chapter_pages_scraped += 1
        self.spider_instance.save()

    def errback(self, failure):
        self.logger.error(repr(failure))
        if failure.check(TimeoutError) or failure.check(HttpError):
            proxy = failure.request.meta.get("proxy")
            if proxy_exists(proxy) and not self.use_proxy:
                return scrapy.Request(
                    failure.request.url,
                    callback=self.parse,
                    errback=self.errback,
                    dont_filter=True,
                    headers={"User-Agent": self.user_agent_fetcher.random},
                )
