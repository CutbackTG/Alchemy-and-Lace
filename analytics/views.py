from datetime import timedelta

from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone

from .models import PageView


def staff_required(user):
    return (
        user.is_authenticated
        and user.is_staff
    )


@user_passes_test(staff_required)
def dashboard(request):
    now = timezone.now()
    today = timezone.localdate()

    seven_days_ago = (
        now - timedelta(days=7)
    )

    thirty_days_ago = (
        now - timedelta(days=30)
    )

    all_views = PageView.objects.all()

    today_views = all_views.filter(
        timestamp__date=today
    )

    seven_day_views = all_views.filter(
        timestamp__gte=seven_days_ago
    )

    thirty_day_views = all_views.filter(
        timestamp__gte=thirty_days_ago
    )

    top_pages = (
        seven_day_views
        .values("path")
        .annotate(
            views=Count("id"),
            visitors=Count(
                "visitor_key",
                distinct=True,
            ),
        )
        .order_by("-views")[:10]
    )

    referrers = (
        seven_day_views
        .exclude(referrer_host="")
        .values("referrer_host")
        .annotate(
            visits=Count("id")
        )
        .order_by("-visits")[:10]
    )

    devices = (
        seven_day_views
        .values("device")
        .annotate(
            visits=Count("id")
        )
        .order_by("-visits")
    )

    context = {
        "pageviews_today": (
            today_views.count()
        ),
        "visitors_today": (
            today_views
            .values("visitor_key")
            .distinct()
            .count()
        ),

        "pageviews_7_days": (
            seven_day_views.count()
        ),
        "visitors_7_days": (
            seven_day_views
            .values(
                "timestamp__date",
                "visitor_key",
            )
            .distinct()
            .count()
        ),

        "pageviews_30_days": (
            thirty_day_views.count()
        ),

        "top_pages": top_pages,
        "referrers": referrers,
        "devices": devices,
    }

    return render(
        request,
        "analytics/dashboard.html",
        context,
    )