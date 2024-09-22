import scrapy
import proxy_manager.models as pm_models
import cout.native.console as cout
from fake_useragent import UserAgent


class ProxyValidatorSpider(scrapy.Spider):
    name = "proxy_validator_spider"
    user_agent_fetcher = UserAgent(browsers="firefox")
    start_urls = []

    def __init__(
        self,
        test_url,
        proxies,
        *args,
        **kwargs,
    ):
        self.test_url = test_url
        self.proxies = proxies
        self.start_urls.append(self.test_url)
        self.cout = cout.ConsoleOut(header="SC_BOTS::PROXY_VALIDATOR_SPIDER")
        super().__init__(*args, **kwargs)
        self.cout.broadcast(style="success", message="Successfully initialized.")

    def start_requests(self):
        super().start_requests()
        for proxy in self.proxies:
            yield scrapy.Request(
                url=self.test_url,
                callback=self.parse,
                dont_filter=True,
                errback=self.errback,
                meta={
                    "proxy": proxy,
                    "download_timeout": 5,
                },
                headers={"User-Agent": self.user_agent_fetcher.random},
            )

    def parse(self, response):
        proxy_schema = response.request.meta.get("proxy")
        if response.status == 200:
            pm_models.add_proxy_schema(proxy_schema)
        else:
            if pm_models.Proxy.objects.filter(schema=proxy_schema).count() > 0:
                pm_models.Proxy.objects.get(schema=proxy_schema).delete()

    def errback(self, failure):
        self.logger.error(repr(failure))
        proxy_schema = failure.request.meta.get("proxy")
        if pm_models.Proxy.objects.filter(schema=proxy_schema).count() > 0:
            print(cout.ConsoleColors.CRED + cout.ConsoleColors.CBOLD)
            print(proxy_schema)
            print(cout.ConsoleColors.CEND)
            pm_models.Proxy.objects.get(schema=proxy_schema).delete()
