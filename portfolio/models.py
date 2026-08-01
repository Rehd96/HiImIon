from django.db import models


class PageView(models.Model):
    """One row per non-static request. The panel reads nothing else."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    path = models.CharField(max_length=500, db_index=True)
    # Set when the request resolved to a project page — makes per-project
    # counts a plain GROUP BY instead of parsing paths at read time.
    project_slug = models.CharField(max_length=100, blank=True, db_index=True)
    status = models.PositiveSmallIntegerField(default=200)
    latency_ms = models.PositiveIntegerField(default=0)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=400, blank=True)
    referer = models.CharField(max_length=500, blank=True)
    is_bot = models.BooleanField(default=False, db_index=True)
    # Rotating per-day hash of (ip + user agent): lets us count unique visitors
    # without storing anything that identifies one across days.
    visitor_hash = models.CharField(max_length=32, blank=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at', 'is_bot']),
        ]

    def __str__(self):
        return f'{self.created_at:%Y-%m-%d %H:%M} {self.path}'

    @property
    def referer_host(self):
        if not self.referer:
            return ''
        stripped = self.referer.split('//', 1)[-1]
        return stripped.split('/', 1)[0]
