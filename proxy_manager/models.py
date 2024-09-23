import random
from django.db import models


class Proxy(models.Model):
    schema = models.CharField(max_length=512)


def add_proxy_schema(proxy_schema):
    Proxy.objects.get_or_create(schema=proxy_schema)


def get_random():
    if Proxy.objects.count() > 0:
        return random.choice([proxy.schema for proxy in Proxy.objects.all()])
    return None


def modify_with_proxy(request):
    proxy = get_random()
    if proxy is None:
        return request
    request.meta["proxy"] = proxy
    return request


def proxy_exists(proxy_schema):
    return proxy_schema in [proxy.schema for proxy in Proxy.objects.all()]
