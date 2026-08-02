import hashlib
import time

from django.utils import timezone

# /healthz is polled by the VPS monitor agent every 30 seconds. Recording that
# would add ~2,900 rows a day and bury the real traffic in the panel.
SKIP_PREFIXES = ('/static/', '/media/', '/favicon', '/django-admin/', '/healthz')

# Substrings that mean "not a person". Checked lowercased; kept short and
# obvious rather than exhaustive — the panel can filter bots either way.
BOT_MARKERS = (
    'bot', 'crawler', 'spider', 'slurp', 'curl/', 'wget', 'python-requests',
    'httpx', 'go-http-client', 'headlesschrome', 'lighthouse', 'monitor',
    'uptime', 'scrapy', 'facebookexternalhit', 'preview', 'fetcher',
)


def client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '').strip()
    return (
        forwarded.split(',')[0].strip()
        or request.META.get('HTTP_X_REAL_IP', '').strip()
        or request.META.get('REMOTE_ADDR', '')
        or ''
    )


def looks_like_bot(user_agent):
    if not user_agent:
        return True
    ua = user_agent.lower()
    return any(marker in ua for marker in BOT_MARKERS)


def daily_visitor_hash(ip, user_agent):
    """Salted with the date, so the hash cannot follow anyone past midnight."""
    raw = f'{timezone.localdate().isoformat()}|{ip}|{user_agent}'
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:32]


class PageViewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if request.method != 'GET' or any(path.startswith(p) for p in SKIP_PREFIXES):
            return self.get_response(request)

        start = time.monotonic()
        response = self.get_response(request)
        latency_ms = int((time.monotonic() - start) * 1000)

        # Never let analytics break a page.
        try:
            self.record(request, response, latency_ms)
        except Exception:
            pass

        return response

    def record(self, request, response, latency_ms):
        from .models import PageView

        # The panel is mine; logging my own clicks would poison the numbers.
        if request.path.startswith('/panel/'):
            return

        ip = client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:400]

        PageView.objects.create(
            path=request.path[:500],
            project_slug=getattr(request, 'project_slug', '') or '',
            status=response.status_code,
            latency_ms=latency_ms,
            ip=ip or None,
            user_agent=user_agent,
            referer=request.META.get('HTTP_REFERER', '')[:500],
            is_bot=looks_like_bot(user_agent),
            visitor_hash=daily_visitor_hash(ip, user_agent),
        )
