import hashlib
import hmac
from urllib.parse import urlparse

from django.conf import settings
from django.utils import timezone

from .models import PageView


IGNORED_PATHS = (
    "/admin/",
    "/analytics/",
    "/static/",
    "/media/",
    "/favicon.ico",
    "/robots.txt",
)


BOT_MARKERS = (
    "bot",
    "crawler",
    "spider",
    "slurp",
    "bingpreview",
    "facebookexternalhit",
    "whatsapp",
    "telegrambot",
    "discordbot",
)


def _get_ip(request):
    forwarded = request.META.get(
        "HTTP_X_FORWARDED_FOR",
        "",
    )

    if forwarded:
        return forwarded.split(",")[0].strip()

    return request.META.get(
        "REMOTE_ADDR",
        "",
    )


def _visitor_key(request):
    """
    Create a one-way anonymous visitor identifier.

    It changes every day, preventing long-term visitor tracking.
    Raw IP addresses and user-agent strings are not stored.
    """

    ip = _get_ip(request)

    user_agent = request.META.get(
        "HTTP_USER_AGENT",
        "",
    )

    day = timezone.localdate().isoformat()

    message = (
        f"{day}|{ip}|{user_agent}"
    ).encode("utf-8")

    digest = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        message,
        hashlib.sha256,
    ).hexdigest()

    return digest[:32]


def _device_type(user_agent):
    ua = user_agent.lower()

    if "ipad" in ua or "tablet" in ua:
        return "tablet"

    if any(
        marker in ua
        for marker in (
            "iphone",
            "android",
            "mobile",
        )
    ):
        return "mobile"

    if ua:
        return "desktop"

    return "other"


def _is_bot(user_agent):
    ua = user_agent.lower()

    return any(
        marker in ua
        for marker in BOT_MARKERS
    )


def _referrer_host(request):
    referrer = request.META.get(
        "HTTP_REFERER",
        "",
    )

    if not referrer:
        return ""

    try:
        hostname = (
            urlparse(referrer).hostname
            or ""
        ).lower()
    except ValueError:
        return ""

    try:
        current_host = (
            request.get_host()
            .split(":")[0]
            .lower()
        )
    except Exception:
        current_host = ""

    # Don't count movement around our own website
    # as an external traffic source.
    if hostname == current_host:
        return ""

    return hostname[:255]


class AnalyticsMiddleware:
    """
    Record anonymous aggregate storefront traffic.

    Analytics failure must never interrupt the shop.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        try:
            self._record(
                request,
                response,
            )
        except Exception:
            # Analytics must never be capable of
            # breaking the customer-facing site.
            pass

        return response

    def _record(self, request, response):
        if request.method != "GET":
            return

        if response.status_code != 200:
            return

        path = request.path

        if path.startswith(IGNORED_PATHS):
            return

        content_type = response.get(
            "Content-Type",
            "",
        )

        if "text/html" not in content_type:
            return

        user_agent = request.META.get(
            "HTTP_USER_AGENT",
            "",
        )

        if _is_bot(user_agent):
            return

        PageView.objects.create(
            path=path[:500],
            referrer_host=_referrer_host(
                request
            ),
            device=_device_type(
                user_agent
            ),
            visitor_key=_visitor_key(
                request
            ),
        )