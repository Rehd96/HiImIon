# labustagialla.it — portfolio

The landing page for my projects, plus a private analytics panel.
Django 5.1 + SQLite, plain templates, no build step — same shape as
[writerblog](https://github.com/Rehd96/writerblog), which is where the
access-logging pattern comes from.

- **`/`** — landing page, one card per project
- **`/projects/<slug>/`** — a case study per project, with links to GitHub and the live instance
- **`/about/`** — about page
- **`/panel/`** — login-protected analytics: views, unique visitors, per-project breakdown, referrers, raw log

## Local development

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python manage.py migrate
./venv/bin/python manage.py createsuperuser     # must be a superuser or staff
./venv/bin/python manage.py runserver           # http://127.0.0.1:8000
./venv/bin/python manage.py test portfolio      # 25 tests
```

`DJANGO_DEBUG` defaults to true locally, false anywhere the env sets it.

## Editing content

All six projects live in **`portfolio/projects.py`** as plain dicts — prose,
stack, links, status. Nothing project-related is in the database, so editing the
site is editing that one file and restarting.

Adding a project: append a dict. `slug` becomes the URL, `accent` colours the
page, `status` is one of `live` / `active` / `private` / `archived`, and `repo`
is appended to `github.com/Rehd96/`.

## Architecture

| Path | Responsibility |
|---|---|
| `portfolio/projects.py` | The six projects, as data. The only file you edit for content. |
| `portfolio/views.py` | Public pages. Sets `request.project_slug` so views can be attributed. |
| `portfolio/panel_views.py` | Login + the analytics dashboard and raw log. |
| `portfolio/middleware.py` | Records one `PageView` per GET. Skips static, `/panel/`, and non-GET. |
| `portfolio/models.py` | `PageView` — the only model. |
| `portfolio/storage.py` | Manifest static storage that degrades instead of 500ing. |
| `templates/site/` | Public templates. |
| `templates/panel/` | Panel templates. |
| `static/css/` | Two stylesheets, `site.css` and `panel.css`. |

### Analytics, and what is not collected

Every GET is written to `PageView`: path, status, latency, IP, user agent,
referrer, and a `visitor_hash`.

That hash is `sha256(today's date + IP + user agent)`. It makes unique-visitor
counts possible **within** a day and deliberately impossible **across** days —
the salt rotates at midnight, so there is no identifier that follows anyone.
There are no cookies, no third-party analytics, and no tracking script; the
panel is the only consumer of any of it.

Hits on `/panel/` are never recorded — otherwise my own clicks would dominate
the numbers. Bots are recorded but flagged, and hidden from the dashboard unless
you toggle them on.

Retention is `PAGEVIEW_RETENTION_DAYS` (400 by default), enforced by cron:

```cron
17 4 * * * cd /home/ion/HiImIon && ./venv/bin/python manage.py prune_views >> /var/log/hiimion-prune.log 2>&1
```

## Deploying

Full walkthrough in [`DEPLOY.md`](DEPLOY.md). Short version, on the VPS:

```bash
cd ~/HiImIon && ./deploy/deploy.sh
```

The app binds `127.0.0.1:8010` under systemd; nginx terminates TLS and serves
`/static/` directly. The existing `/cff`, `/fai` and `/ezbk` subpaths are
untouched — nginx matches those more specific prefixes first.
