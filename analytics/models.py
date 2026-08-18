from django.db import models


class PageView(models.Model):
    DEVICE_CHOICES = [
        ("desktop", "Desktop"),
        ("mobile", "Mobile"),
        ("tablet", "Tablet"),
        ("other", "Other"),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)

    path = models.CharField(
        max_length=500,
        db_index=True,
    )

    referrer_host = models.CharField(
        max_length=255,
        blank=True,
    )

    device = models.CharField(
        max_length=20,
        choices=DEVICE_CHOICES,
        default="other",
    )

    # Anonymous identifier that changes every day.
    # Raw IP addresses and user agents are never stored.
    visitor_key = models.CharField(
        max_length=32,
        db_index=True,
    )

    class Meta:
        ordering = ["-timestamp"]

        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["path", "timestamp"]),
            models.Index(fields=["visitor_key", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.path} - {self.timestamp:%Y-%m-%d %H:%M}"