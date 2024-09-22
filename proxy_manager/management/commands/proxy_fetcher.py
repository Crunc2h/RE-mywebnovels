import proxy_manager.models as pm_models
from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from sc_bots.sc_bots.spiders.proxy_validator_spider import ProxyValidatorSpider
from ballyregan.models import Protocols, Anonymities
from ballyregan import ProxyFetcher


class Command(BaseCommand):
    def handle(self, *args, **options):
        fetcher = ProxyFetcher(debug=True)
        proxies = fetcher.get(
            limit=2,
            anonymities=[Anonymities.ELITE, Anonymities.ANONYMOUS, Anonymities.UNKNOWN],
            protocols=[
                Protocols.HTTPS,
            ],
        )

        present_proxies = [
            present_proxy.schema for present_proxy in pm_models.Proxy.objects.all()
        ]
        proxies = [
            f"{proxy.protocol}://{proxy.ip}:{proxy.port}"
            for proxy in proxies
            if f"{proxy.protocol}://{proxy.ip}:{proxy.port}" not in present_proxies
        ]
        if len(proxies) == 0:
            return

        process = CrawlerProcess()
        process.settings["LOG_ENABLED"] = True
        process.crawl(
            ProxyValidatorSpider,
            test_url="https://www.webnovelpub.pro/",
            proxies=proxies,
        )
        process.start()
