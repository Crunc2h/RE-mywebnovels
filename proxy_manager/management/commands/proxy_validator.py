import proxy_manager.models as pm_models
from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from sc_bots.sc_bots.spiders.proxy_validator_spider import ProxyValidatorSpider


class Command(BaseCommand):
    def handle(self, *args, **options):
        if pm_models.Proxy.objects.count() == 0:
            return
        process = CrawlerProcess()
        process.settings["LOG_ENABLED"] = True
        process.crawl(
            ProxyValidatorSpider,
            test_url="https://www.webnovelpub.pro/",
            proxies=[proxy.schema for proxy in pm_models.Proxy.objects.all()],
        )
        process.start()
