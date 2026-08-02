from django.http import Http404, HttpResponse
from django.shortcuts import render

from . import projects as project_data


def home(request):
    return render(request, 'site/home.html', {
        'projects': project_data.all_projects(),
    })


def project_detail(request, slug):
    project = project_data.get_project(slug)
    if not project:
        raise Http404('No such project')

    # Read by PageViewMiddleware so per-project counts are a GROUP BY.
    request.project_slug = slug

    previous, following = project_data.neighbours(slug)
    return render(request, 'site/project.html', {
        'project': project,
        'previous': previous,
        'next': following,
    })


def about(request):
    return render(request, 'site/about.html', {
        'projects': project_data.all_projects(),
    })


# This is the ONLY robots.txt on labustagialla.it — crawlers read it at the
# domain root, and the root belongs to this app. The blog (writerblog, mounted
# at /blog/) and rentwatch (at /case/) deliberately serve none of their own, so
# their policy has to live here; both are gated, and must stay out of search
# results.
ROBOTS = """User-agent: *
Disallow: /panel/
Disallow: /django-admin/
Disallow: /blog/
Disallow: /case/

# No thanks.
User-agent: GPTBot
Disallow: /
User-agent: ChatGPT-User
Disallow: /
User-agent: OAI-SearchBot
Disallow: /
User-agent: ClaudeBot
Disallow: /
User-agent: anthropic-ai
Disallow: /
User-agent: Google-Extended
Disallow: /
User-agent: CCBot
Disallow: /
User-agent: Bytespider
Disallow: /
User-agent: PerplexityBot
Disallow: /
User-agent: Applebot-Extended
Disallow: /
User-agent: Amazonbot
Disallow: /
User-agent: FacebookBot
Disallow: /
"""


def robots(request):
    return HttpResponse(ROBOTS, content_type='text/plain')


def healthz(request):
    """Liveness probe for the VPS monitor agent.

    Deliberately not the homepage: the agent polls every 30 seconds, and
    PageViewMiddleware skips this path so the panel keeps counting people
    rather than the monitoring.
    """
    return HttpResponse('ok', content_type='text/plain')
