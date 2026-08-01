from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.shortcuts import redirect, render
from django.utils import timezone

from . import projects as project_data
from .models import PageView

RANGES = {'1': 1, '7': 7, '30': 30, '90': 90, '365': 365}
DEFAULT_RANGE = '30'


def _staff_only(view):
    """login_required plus a staff check — the panel has no non-staff users."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            logout(request)
            return redirect('panel_login')
        return view(request, *args, **kwargs)
    return wrapper


def panel_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('panel_dashboard')

    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username', '').strip(),
            password=request.POST.get('password', ''),
        )
        if user and user.is_staff:
            login(request, user)
            return redirect('panel_dashboard')
        messages.error(request, 'Wrong username or password.')

    return render(request, 'panel/login.html')


def panel_logout(request):
    logout(request)
    return redirect('home')


def _window(request):
    """(days, key) from ?range=, defaulting to 30."""
    key = request.GET.get('range', DEFAULT_RANGE)
    if key not in RANGES:
        key = DEFAULT_RANGE
    return RANGES[key], key


def _base_queryset(request):
    """Everything in the window, bots excluded unless ?bots=1."""
    days, _ = _window(request)
    since = timezone.now() - timedelta(days=days)
    qs = PageView.objects.filter(created_at__gte=since)
    if request.GET.get('bots') != '1':
        qs = qs.filter(is_bot=False)
    return qs


def _count_since(days, include_bots):
    qs = PageView.objects.filter(created_at__gte=timezone.now() - timedelta(days=days))
    if not include_bots:
        qs = qs.filter(is_bot=False)
    return qs.count()


@_staff_only
def dashboard(request):
    days, range_key = _window(request)
    include_bots = request.GET.get('bots') == '1'
    qs = _base_queryset(request)

    # ── Daily series, zero-filled so the chart has no gaps ──────────────
    counts = dict(
        qs.annotate(day=TruncDate('created_at'))
          .values('day')
          .annotate(n=Count('id'))
          .values_list('day', 'n')
    )
    today = timezone.localdate()
    series = [
        {'date': today - timedelta(days=offset),
         'count': counts.get(today - timedelta(days=offset), 0)}
        for offset in range(days - 1, -1, -1)
    ]
    peak = max((point['count'] for point in series), default=0) or 1
    for point in series:
        point['height'] = round(point['count'] / peak * 100)

    # ── Per-project views ───────────────────────────────────────────────
    project_counts = dict(
        qs.exclude(project_slug='')
          .values('project_slug')
          .annotate(n=Count('id'))
          .values_list('project_slug', 'n')
    )
    project_uniques = dict(
        qs.exclude(project_slug='')
          .values('project_slug')
          .annotate(n=Count('visitor_hash', distinct=True))
          .values_list('project_slug', 'n')
    )
    project_rows = sorted(
        (
            {
                'name': p['name'],
                'slug': p['slug'],
                'accent': p['accent'],
                'views': project_counts.get(p['slug'], 0),
                'visitors': project_uniques.get(p['slug'], 0),
            }
            for p in project_data.all_projects()
        ),
        key=lambda row: -row['views'],
    )
    project_peak = max((row['views'] for row in project_rows), default=0) or 1
    for row in project_rows:
        row['width'] = round(row['views'] / project_peak * 100)

    # ── Top paths and referrers ─────────────────────────────────────────
    top_paths = list(
        qs.values('path').annotate(n=Count('id')).order_by('-n')[:12]
    )
    referrers = {}
    for view in qs.exclude(referer='').only('referer').iterator():
        host = view.referer_host
        if host:
            referrers[host] = referrers.get(host, 0) + 1
    top_referrers = sorted(referrers.items(), key=lambda kv: -kv[1])[:10]

    stats = {
        'today': _count_since(1, include_bots),
        'window': qs.count(),
        'visitors': qs.values('visitor_hash').distinct().count(),
        'all_time': PageView.objects.count(),
        'bots': PageView.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=days), is_bot=True
        ).count(),
        'errors': qs.filter(status__gte=400).count(),
    }

    return render(request, 'panel/dashboard.html', {
        'stats': stats,
        'series': series,
        'project_rows': project_rows,
        'top_paths': top_paths,
        'top_referrers': top_referrers,
        'range_key': range_key,
        'range_days': days,
        'include_bots': include_bots,
        'recent': qs[:15],
    })


@_staff_only
def view_log(request):
    """The raw hits, paginated — for when the aggregates are not enough."""
    qs = _base_queryset(request)

    path_filter = request.GET.get('path', '').strip()
    if path_filter:
        qs = qs.filter(path__icontains=path_filter)

    _, range_key = _window(request)
    page = Paginator(qs, 100).get_page(request.GET.get('page'))

    return render(request, 'panel/views.html', {
        'page': page,
        'range_key': range_key,
        'include_bots': request.GET.get('bots') == '1',
        'path_filter': path_filter,
    })
