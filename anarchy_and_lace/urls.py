from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

from .sitemaps import (
    CollectionSitemap,
    ProductSitemap,
    StaticSitemap,
)

sitemaps = {
    "static": StaticSitemap,
    "collections": CollectionSitemap,
    "products": ProductSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("shop/", include("catalog.urls")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("", include(("home.urls", "home"), namespace="home")),
    path("analytics/", include("analytics.urls"),
),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

path(
    "robots.txt",
    TemplateView.as_view(
        template_name="robots.txt",
        content_type="text/plain",
    ),
),