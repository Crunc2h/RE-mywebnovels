import scrapy
import spiders_manager.models as sm_models
import novels_storage.models as ns_models
import cout.native.console as cout
from twisted.internet.error import TimeoutError
from scrapy.spidermiddlewares.httperror import HttpError
from proxy_manager.models import modify_with_proxy, proxy_exists
from pathlib import Path
from fake_useragent import UserAgent


FILE_FORMAT = "html"
CHAPTER_LINK_PAGES_FORMAT = "/chapter_links_page-{current_page}.{file_format}"


class ChapterLinkPagesSpider(scrapy.Spider):
    name = "chapter_link_pages_spider"
    start_urls = []
    user_agent_fetcher = UserAgent(browsers="firefox")
    download_delay = 0.5

    def __init__(
        self,
        process_id,
        website_name,
        novel_page_urls_to_chapter_link_page_directories,
        get_chapters_index_page,
        get_next_page,
        get_max_page,
        use_proxy=False,
        *args,
        **kwargs,
    ):
        self.process_id = process_id
        self.website_name = website_name
        self.website = ns_models.Website.objects.get(name=self.website_name)
        self.update_process_instance = (
            self.website.update_instance.process_instances.get(
                process_id=self.process_id
            )
        )
        self.spider_instance = sm_models.UpdateSpiderInstance(
            update_process_instance=self.update_process_instance
        )
        self.spider_instance.save()

        self.get_chapters_index_page = get_chapters_index_page
        self.get_next_page = get_next_page
        self.get_max_page = get_max_page
        self.novel_page_urls_to_chapter_link_page_directories = (
            novel_page_urls_to_chapter_link_page_directories
        )
        self.cout = cout.ConsoleOut(header="SC_BOTS::CHAPTER_LINK_PAGES_SPIDER")

        self.start_urls.extend(
            list(novel_page_urls_to_chapter_link_page_directories.keys())
        )

        super().__init__(*args, **kwargs)
        self.cout.broadcast(style="success", message="Successfully initialized.")

    def start_requests(self):
        super().start_requests()
        for url in self.start_urls:
            if self.use_proxy:
                yield modify_with_proxy(
                    scrapy.Request(
                        url,
                        self.parse,
                        dont_filter=True,
                        headers={"User-Agent": self.user_agent_fetcher.random},
                    )
                )
            else:
                yield scrapy.Request(
                    url,
                    self.parse,
                    dont_filter=True,
                    headers={"User-Agent": self.user_agent_fetcher.random},
                )

    def parse(self, response):
        self.current_novel_page_url = response.url
        self.chapter_link_pages_directory = (
            self.novel_page_urls_to_chapter_link_page_directories[
                self.current_novel_page_url
            ]
        )
        self.cout.broadcast(
            style="progress",
            message=f"<{response.status}> Navigating to chapters index page of {self.current_novel_page_url}...",
        )

        chapters_index_page_url = self.get_chapters_index_page(
            response, self.website.link_object.base_link
        )
        if chapters_index_page_url is None:
            raise Exception("No chapters index page!")
        if self.use_proxy:
            return modify_with_proxy(
                scrapy.Request(
                    chapters_index_page_url,
                    self.parse_chapter_link_page,
                    dont_filter=True,
                    headers={"User-Agent": self.user_agent_fetcher.random},
                )
            )
        else:
            return scrapy.Request(
                chapters_index_page_url,
                self.parse_chapter_link_page,
                dont_filter=True,
                headers={"User-Agent": self.user_agent_fetcher.random},
            )

    def parse_chapter_link_page(self, response):
        self.cout.broadcast(
            style="progress",
            message=f"<{response.status}> Crawling {response.url}...",
        )
        max_page = self.get_max_page(response, self.website.link_object.base_link)
        if max_page is None:
            raise Exception("NO MAX PAGE")

        Path(
            self.chapter_link_pages_directory
            + CHAPTER_LINK_PAGES_FORMAT.format(
                current_page=self.spider_instance.chapter_link_pages_scraped,
                file_format=FILE_FORMAT,
            )
        ).write_bytes(response.body)

        self.spider_instance.chapter_link_pages_scraped += 1
        self.spider_instance.save()
        next_page = self.get_next_page(response, self.website.link_object.base_link)

        if not next_page:
            if max_page == response.url:
                self.cout.broadcast(
                    style="success",
                    message=f"Crawling of chapter link pages from {self.current_novel_page_url} is complete.",
                )
                return
            ##DEBUG
            print(
                f"{cout.ConsoleColors.CRED}{cout.ConsoleColors.CBOLD}++++++++++++++++++++++++++"
            )
            print(max_page)
            print(response.url)
            print(cout.ConsoleColors.CEND)
            ##DEBUG
            raise Exception("Didnt scrape the whole content!!!")
        else:
            if self.use_proxy:
                return modify_with_proxy(
                    scrapy.Request(
                        next_page,
                        self.parse_chapter_link_page,
                        dont_filter=True,
                        headers={"User-Agent": self.user_agent_fetcher.random},
                    )
                )
            else:
                return scrapy.Request(
                    next_page,
                    self.parse_chapter_link_page,
                    dont_filter=True,
                    headers={"User-Agent": self.user_agent_fetcher.random},
                )

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
