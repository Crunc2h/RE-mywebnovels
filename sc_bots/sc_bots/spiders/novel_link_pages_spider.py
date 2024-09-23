import scrapy
import spiders_manager.models as sm_models
import novels_storage.models as ns_models
import cout.native.console as cout
from pathlib import Path
from proxy_manager.models import modify_with_proxy, proxy_exists
from twisted.internet.error import TimeoutError
from scrapy.spidermiddlewares.httperror import HttpError
from fake_useragent import UserAgent

UA = UserAgent()
FILE_FORMAT = "html"
NOVEL_LINKS_PAGE_FORMAT = "/novel_links_page-{current_page}.{file_format}"


class NovelLinkPagesSpider(scrapy.Spider):
    name = "novel_link_pages_spider"
    start_urls = []
    user_agent_fetcher = UserAgent(browsers="firefox")
    max_page = None

    def __init__(
        self,
        process_id,
        website_name,
        novel_link_pages_directory,
        website_crawler_start_url,
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
        self.use_proxy = use_proxy
        self.spider_instance = sm_models.UpdateSpiderInstance(
            update_process_instance=self.update_process_instance
        )
        self.spider_instance.save()

        self.novel_link_pages_directory = novel_link_pages_directory
        self.get_next_page = get_next_page
        self.get_max_page = get_max_page

        self.start_urls.append(website_crawler_start_url)
        super().__init__(*args, **kwargs)

        self.cout = cout.ConsoleOut(header="SC_BOTS::NOVEL_LINK_PAGES_SPIDER")
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
        self.cout.broadcast(
            style="progress",
            message=f"<{response.status}> Crawling {response.url}...",
        )

        if self.max_page is None:
            self.max_page = self.get_max_page(
                response, self.website.link_object.base_link
            )
            if self.max_page is None:
                raise Exception("NO MAX PAGE")

        Path(
            self.novel_link_pages_directory
            + NOVEL_LINKS_PAGE_FORMAT.format(
                current_page=self.spider_instance.novel_link_pages_scraped,
                file_format=FILE_FORMAT,
            )
        ).write_bytes(response.body)

        self.spider_instance.novel_link_pages_scraped += 1
        self.spider_instance.save()

        next_page = self.get_next_page(response, self.website.link_object.base_link)
        if not next_page:
            if self.max_page == response.url:
                self.cout.broadcast(
                    style="success",
                    message=f"Crawling of novel link pages from {self.start_urls[0]}",
                )
                return
            raise Exception("Didnt scrape the whole content!!!")
        else:
            if not self.use_proxy:
                return scrapy.Request(
                    next_page,
                    self.parse,
                    errback=self.errback,
                    dont_filter=True,
                    headers={"User-Agent": self.user_agent_fetcher.random},
                )
            else:
                return modify_with_proxy(
                    scrapy.Request(
                        next_page,
                        self.parse,
                        errback=self.errback,
                        dont_filter=True,
                        headers={"User-Agent": self.user_agent_fetcher.random},
                    )
                )

    def errback(self, failure):
        self.logger.error(repr(failure))
        if failure.check(TimeoutError) or failure.check(HttpError):
            proxy = failure.request.meta.get("proxy")
            if proxy_exists(proxy) and not self.use_proxy:
                return scrapy.Request(
                    failure.request.url,
                    self.parse,
                    errback=self.errback,
                    dont_filter=True,
                    headers={"User-Agent": self.user_agent_fetcher.random},
                )
