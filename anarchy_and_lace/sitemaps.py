from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from catalog.shopify import get_products


class StaticSitemap(Sitemap):
    protocol = "https"

    def items(self):
        return [
            "home:home",
            "catalog:shop",
            "home:kimono_history",
            "home:contact",
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        priorities = {
            "home:home": 1.0,
            "catalog:shop": 0.9,
            "home:kimono_history": 0.7,
            "home:contact": 0.5,
        }

        return priorities.get(item, 0.5)


class CollectionSitemap(Sitemap):
    protocol = "https"
    priority = 0.8
    changefreq = "daily"

    def items(self):
        return [
            "anarchy",
            "lace",
        ]

    def location(self, collection_handle):
        return reverse(
            "catalog:collection_detail",
            kwargs={
                "collection_handle": collection_handle,
            },
        )


class ProductSitemap(Sitemap):
    protocol = "https"
    priority = 0.9
    changefreq = "weekly"

    def items(self):
        try:
            return get_products()
        except Exception:
            return []

    def location(self, product):
        return reverse(
            "catalog:product_detail",
            kwargs={
                "slug": product["handle"],
            },
        )