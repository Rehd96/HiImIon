from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from . import projects as project_data
from .middleware import looks_like_bot
from .models import PageView

BROWSER_UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')


class PublicSiteTests(TestCase):
    def test_home_lists_every_project(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        for project in project_data.PROJECTS:
            self.assertContains(response, project['name'])

    def test_every_project_page_renders(self):
        for project in project_data.PROJECTS:
            with self.subTest(slug=project['slug']):
                response = self.client.get(f'/projects/{project["slug"]}/')
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, project['tagline'])
                # The GitHub link is the whole point of the page.
                self.assertContains(
                    response,
                    f'https://github.com/{project_data.GITHUB_USER}/{project["repo"]}',
                )

    def test_unknown_project_is_404(self):
        self.assertEqual(self.client.get('/projects/nope/').status_code, 404)

    def test_about_and_robots(self):
        self.assertEqual(self.client.get('/about/').status_code, 200)
        robots = self.client.get('/robots.txt')
        self.assertEqual(robots['Content-Type'], 'text/plain')
        self.assertContains(robots, 'Disallow: /panel/')
        # The blog and rentwatch serve no robots.txt of their own — their
        # policy lives here, at the only root a crawler will ask.
        self.assertContains(robots, 'Disallow: /blog/')
        self.assertContains(robots, 'Disallow: /case/')


class PageViewLoggingTests(TestCase):
    def test_view_is_recorded_with_project_slug(self):
        self.client.get('/projects/rentwatch/', HTTP_USER_AGENT=BROWSER_UA)
        view = PageView.objects.get()
        self.assertEqual(view.path, '/projects/rentwatch/')
        self.assertEqual(view.project_slug, 'rentwatch')
        self.assertFalse(view.is_bot)
        self.assertTrue(view.visitor_hash)

    def test_home_has_no_project_slug(self):
        self.client.get('/', HTTP_USER_AGENT=BROWSER_UA)
        self.assertEqual(PageView.objects.get().project_slug, '')

    def test_panel_and_static_are_not_logged(self):
        self.client.get('/panel/login/', HTTP_USER_AGENT=BROWSER_UA)
        self.client.get('/static/css/site.css', HTTP_USER_AGENT=BROWSER_UA)
        self.assertEqual(PageView.objects.count(), 0)

    def test_healthz_is_not_logged(self):
        # The monitor agent polls this every 30s; counting it would drown the
        # panel in ~2,900 rows a day.
        response = self.client.get('/healthz', HTTP_USER_AGENT=BROWSER_UA)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PageView.objects.count(), 0)

    def test_404s_are_logged_with_their_status(self):
        self.client.get('/projects/nope/', HTTP_USER_AGENT=BROWSER_UA)
        self.assertEqual(PageView.objects.get().status, 404)

    def test_bot_detection(self):
        self.assertTrue(looks_like_bot('Googlebot/2.1'))
        self.assertTrue(looks_like_bot('curl/8.5.0'))
        self.assertTrue(looks_like_bot(''))
        self.assertFalse(looks_like_bot(BROWSER_UA))

    def test_visitor_hash_is_stable_within_a_day(self):
        self.client.get('/', HTTP_USER_AGENT=BROWSER_UA)
        self.client.get('/about/', HTTP_USER_AGENT=BROWSER_UA)
        hashes = set(PageView.objects.values_list('visitor_hash', flat=True))
        self.assertEqual(len(hashes), 1)


class PanelAuthTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('ion', password='pw-for-tests', is_staff=True)
        User.objects.create_user('guest', password='pw-for-tests')

    def test_panel_requires_login(self):
        for url in ('/panel/', '/panel/views/'):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn('/panel/login/', response['Location'])

    def test_wrong_password_does_not_log_in(self):
        response = self.client.post('/panel/login/',
                                    {'username': 'ion', 'password': 'nope'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Wrong username or password')
        self.assertEqual(self.client.get('/panel/').status_code, 302)

    def test_non_staff_cannot_reach_the_panel(self):
        response = self.client.post('/panel/login/',
                                    {'username': 'guest', 'password': 'pw-for-tests'})
        self.assertContains(response, 'Wrong username or password')

    def test_staff_login_reaches_the_dashboard(self):
        response = self.client.post('/panel/login/',
                                    {'username': 'ion', 'password': 'pw-for-tests'})
        self.assertRedirects(response, '/panel/', target_status_code=200)

    def test_logout_returns_to_the_site(self):
        self.client.force_login(self.staff)
        self.assertRedirects(self.client.post('/panel/logout/'), '/')


class PanelDashboardTests(TestCase):
    def setUp(self):
        self.client.force_login(
            User.objects.create_user('ion', password='pw-for-tests', is_staff=True)
        )
        now = timezone.now()
        PageView.objects.create(path='/projects/rentwatch/', project_slug='rentwatch',
                                visitor_hash='a', user_agent=BROWSER_UA)
        PageView.objects.create(path='/projects/rentwatch/', project_slug='rentwatch',
                                visitor_hash='b', user_agent=BROWSER_UA)
        PageView.objects.create(path='/', visitor_hash='a', referer='https://news.ycombinator.com/x')
        PageView.objects.create(path='/', visitor_hash='bot', is_bot=True)
        old = PageView.objects.create(path='/about/', visitor_hash='c')
        PageView.objects.filter(pk=old.pk).update(created_at=now - timedelta(days=200))

    def test_dashboard_counts_exclude_bots_by_default(self):
        response = self.client.get('/panel/?range=30')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['stats']['window'], 3)
        self.assertEqual(response.context['stats']['bots'], 1)

    def test_bots_toggle_includes_them(self):
        response = self.client.get('/panel/?range=30&bots=1')
        self.assertEqual(response.context['stats']['window'], 4)

    def test_range_window_excludes_older_rows(self):
        self.assertEqual(self.client.get('/panel/?range=7').context['stats']['window'], 3)
        self.assertEqual(self.client.get('/panel/?range=365').context['stats']['window'], 4)

    def test_per_project_rows(self):
        rows = {r['slug']: r for r in self.client.get('/panel/').context['project_rows']}
        self.assertEqual(rows['rentwatch']['views'], 2)
        self.assertEqual(rows['rentwatch']['visitors'], 2)
        self.assertEqual(rows['writerblog']['views'], 0)
        # Every project appears, even at zero.
        self.assertEqual(len(rows), len(project_data.PROJECTS))

    def test_unique_visitors_are_deduplicated(self):
        self.assertEqual(self.client.get('/panel/?range=30').context['stats']['visitors'], 2)

    def test_series_is_zero_filled(self):
        series = self.client.get('/panel/?range=30').context['series']
        self.assertEqual(len(series), 30)
        self.assertEqual(series[-1]['count'], 3)  # today

    def test_referrer_hosts_are_extracted(self):
        referrers = dict(self.client.get('/panel/').context['top_referrers'])
        self.assertEqual(referrers['news.ycombinator.com'], 1)

    def test_bad_range_falls_back_to_default(self):
        self.assertEqual(self.client.get('/panel/?range=evil').context['range_key'], '30')

    def test_raw_log_filters_by_path(self):
        response = self.client.get('/panel/views/?path=rentwatch&range=30')
        self.assertEqual(response.context['page'].paginator.count, 2)


class PruneCommandTests(TestCase):
    def test_prune_deletes_only_old_rows(self):
        from io import StringIO

        from django.core.management import call_command

        fresh = PageView.objects.create(path='/')
        old = PageView.objects.create(path='/old/')
        PageView.objects.filter(pk=old.pk).update(
            created_at=timezone.now() - timedelta(days=500)
        )

        call_command('prune_views', days=400, stdout=StringIO())

        self.assertEqual(list(PageView.objects.values_list('pk', flat=True)), [fresh.pk])
