"""The six projects, as static data.

Content lives here rather than in the database on purpose: it is prose that
belongs in version control, it changes when the code changes, and it means the
admin panel has exactly one job (analytics) instead of being a CMS.

Adding a project = append a dict below. `slug` becomes /projects/<slug>/.
"""

GITHUB_USER = 'Rehd96'

# Status vocabulary → (label, css modifier)
STATUS = {
    'live': ('Live', 'live'),
    'active': ('In development', 'active'),
    'private': ('Live · private', 'private'),
    'archived': ('Archived', 'archived'),
}

PROJECTS = [
    {
        'slug': 'castelfidardo-festival',
        'name': 'Castelfidardo Festival',
        'tagline': 'A full-stack platform for a 51-year-old international music festival.',
        'year': '2026',
        'status': 'live',
        'accent': '#f4b942',
        'repo': 'casterfidarno-festival',
        'live_url': 'https://labustagialla.it/cff',
        'live_label': 'labustagialla.it/cff',
        'role': 'Sole developer — architecture, backend, web, mobile, deployment',
        'stack': ['NestJS', 'Next.js', 'React Native / Expo', 'TypeScript',
                  'PostgreSQL', 'Prisma', 'Redis', 'WebSocket', 'Turborepo',
                  'Docker', 'GitHub Actions', 'nginx'],
        'summary': (
            'The platform behind PIF 2026 — the 51st Premio Internazionale della '
            'Fisarmonica in Castelfidardo, five days and six venues of accordion '
            'music in September 2026. It runs the public programme, guest '
            'registration and bookings, a portal for the B&B and restaurant owners '
            'hosting visitors, an admin dashboard for the organising committee, and '
            'live vehicle tracking for the festival shuttles.'
        ),
        'sections': [
            {
                'heading': 'The problem',
                'body': [
                    'A festival that has run for half a century was still coordinating '
                    'accommodation, restaurant seats and shuttle logistics through phone '
                    'calls and spreadsheets. Roughly 35 events across six venues, guests '
                    'arriving from abroad, and a volunteer committee with no technical '
                    'staff to hand the problem to.',
                    'The brief was not "build a website". It was: give the committee one '
                    'place where a guest can find the programme, book a room and a table, '
                    'and know when the next shuttle leaves — and give the owners and the '
                    'committee the other side of those same screens.',
                ],
            },
            {
                'heading': 'What I built',
                'body': [
                    'A Turborepo monorepo with three deployables sharing one typed '
                    'contract package: a NestJS API, a Next.js web app, and an Expo '
                    'mobile app for Android.',
                    'The booking side is the interesting half. Guests browse and reserve; '
                    'B&B and restaurant owners get a portal where they confirm, decline or '
                    'adjust those reservations against their real availability; the '
                    'committee sees everything and can export the whole dataset from the '
                    'admin dashboard. The transport module tracks two vehicles and pushes '
                    'their positions to every open client over WebSocket.',
                    'The real 2026 programme — every event, venue and artist bio, '
                    'headliners included — ships as typed static data and switches to live '
                    'API content automatically once the committee populates it. That let '
                    'the public site go up months before the admin content workflow was '
                    'finished.',
                ],
            },
            {
                'heading': 'Running it in production',
                'body': [
                    'It shares a VPS with three other applications, so it lives behind '
                    'nginx on the /cff subpath with everything bound to localhost — '
                    'nothing in the stack is reachable except through the proxy.',
                    'Releases are blue/green: the new colour is built and health-checked '
                    'alongside the old one, nginx\'s active upstream is flipped by the '
                    'deploy script, and the previous colour stays up as an instant '
                    'rollback. Push to main and GitHub Actions runs the whole sequence.',
                    'Rate limiting, an AI-crawler block at the edge, a documented threat '
                    'model and an operator runbook came with it — the committee needed to '
                    'be able to lock an account or restore a backup without me.',
                ],
            },
            {
                'heading': 'Where it stands',
                'body': [
                    'The website is live and the Android build is in progress. The honest '
                    'lesson from this one was not technical: getting a build accepted by '
                    'the Play Store — organisation account, D-U-N-S number, the 12-tester '
                    'gate, a package name you can never change — turned out to be a harder '
                    'problem than building the app, and it is documented as its own runbook '
                    'in the repo.',
                ],
            },
        ],
        'highlights': [
            'Three deployables (API, web, mobile) from one typed monorepo',
            'Blue/green zero-downtime deploys with automatic rollback',
            'Live shuttle positions over WebSocket',
            'Two-sided booking flow: guests, venue owners, committee',
        ],
    },
    {
        'slug': 'vps-monitor',
        'name': 'VPS Monitor',
        'tagline': 'I got tired of SSHing in to find out whether anything was down.',
        'year': '2026',
        'status': 'private',
        'accent': '#4ade80',
        'repo': 'festival-monitor',
        'live_url': None,
        'live_label': 'Tailscale-only — no public endpoint',
        'role': 'Sole developer',
        'stack': ['NestJS', 'TypeScript', 'SQLite', 'Prisma', 'TOTP 2FA',
                  'Docker', 'systemd', 'Tailscale'],
        'summary': (
            'A private monitoring dashboard for every service on my VPS. An agent on '
            'the host pushes CPU, RAM, disk and per-service health every 30 seconds; '
            'the dashboard shows 13 services across four applications, and it is '
            'reachable only over Tailscale from my phone.'
        ),
        'sections': [
            {
                'heading': 'The problem',
                'body': [
                    'Four applications ended up sharing one box — the festival platform, '
                    'Fainance Automation, the writer blog and ezBookkeeping — spread across '
                    'Docker containers, a Gunicorn process and a bare Go binary. Finding '
                    'out whether something had fallen over meant opening a terminal.',
                    'I wanted the answer on my phone in two seconds, without exposing a '
                    'monitoring endpoint to the internet and without paying for a hosted '
                    'service to watch a hobby server.',
                ],
            },
            {
                'heading': 'What I built',
                'body': [
                    'Two pieces. A metrics agent that runs on the host under systemd, reads '
                    'CPU, memory and disk straight from /proc, probes each configured '
                    'service, and pushes a snapshot every 30 seconds — written in '
                    'TypeScript with zero runtime dependencies, because the thing that '
                    'watches everything else should have the smallest possible failure '
                    'surface.',
                    'And a NestJS API plus dashboard storing those snapshots in SQLite, '
                    'pruning them at 30 days. The dashboard is deliberately vanilla '
                    'JavaScript with no build step: when a service is down at 23:00 I want '
                    'to edit one file, not run a bundler.',
                    'It knows about blue/green deploys, so the festival stack switching '
                    'colours reads as a normal release rather than half the services '
                    'vanishing.',
                ],
            },
            {
                'heading': 'Keeping it private',
                'body': [
                    'The dashboard is never published: it binds to the Tailscale interface, '
                    'so it exists only inside my own network. Login is a password plus a '
                    'six-digit TOTP code from any authenticator app, verified against '
                    'HS256 JWT sessions.',
                    'The TOTP and pbkdf2 implementations use Node\'s native crypto module '
                    'rather than a dependency — same reasoning as the agent.',
                ],
            },
            {
                'heading': 'Where it stands',
                'body': [
                    'Deployed and watching all four applications. The next phase is '
                    'hardware: an e-ink panel on a Raspberry Pi so the status is just '
                    'visible on a shelf instead of requiring me to unlock a phone.',
                ],
            },
        ],
        'highlights': [
            '13 services across 4 applications, one screen',
            'Zero-dependency metrics agent reading /proc directly',
            'TOTP 2FA on native crypto — no auth library',
            'Not on the public internet at all: Tailscale only',
        ],
    },
    {
        'slug': 'writerblog',
        'name': 'Writer Blog',
        'tagline': 'A publishing platform for a writer who should never see a CMS.',
        'year': '2026',
        'status': 'live',
        'accent': '#c084fc',
        'repo': 'writerblog',
        'live_url': 'https://inclusivortosgt.it',
        'live_label': 'inclusivortosgt.it',
        'role': 'Sole developer',
        'stack': ['Django 5.1', 'Python', 'SQLite', 'Gunicorn', 'nginx',
                  'HTML/CSS (no build step)'],
        'summary': (
            'A personal publishing site: articles, an author page, and a reading '
            'library with star ratings and reviews. Behind it, a hand-built admin '
            'panel that does exactly four things and nothing else — because the '
            'person using it writes books, not software.'
        ),
        'sections': [
            {
                'heading': 'The problem',
                'body': [
                    'A writer needed somewhere to publish, and every off-the-shelf option '
                    'meant handing them a dashboard with forty menu items, a plugin '
                    'updater and a security surface I would end up maintaining.',
                    'The requirement was a site they could run alone, and an editor that '
                    'never asks a question about software.',
                ],
            },
            {
                'heading': 'What I built',
                'body': [
                    'Django 5.1 on SQLite with plain HTML templates — no frontend '
                    'framework and no build step, so deploying is copying files and '
                    'restarting a process.',
                    'The public side is the homepage, a category archive, an about page '
                    'and a Library: a searchable bookshelf with a "currently reading" hero, '
                    'status filters, star ratings and the author\'s own reviews.',
                    'The panel at /panel/ is a custom CRUD surface over exactly four '
                    'models — articles, categories, books, site settings. Django\'s own '
                    'admin stays mounted underneath as a fallback for me, and is locked to '
                    'localhost.',
                    'Themes are part of the product: four palettes and an accent colour, '
                    'driven from a settings singleton through CSS custom properties, so the '
                    'author can restyle the whole site from the panel without touching a '
                    'template.',
                ],
            },
            {
                'heading': 'Hardening it',
                'body': [
                    'A public site with one non-technical operator needs the security to '
                    'be in the infrastructure, not in a habit. nginx rate limits the login '
                    'endpoint, /django-admin/ only answers to localhost, and robots.txt '
                    'blocks the AI crawlers and hides the panel paths.',
                    'Every request is written to an access log table by middleware — IP, '
                    'path, status, latency, user agent, referrer — which turned out to be '
                    'the most useful thing in the project, and is the pattern this '
                    'portfolio site reuses.',
                ],
            },
        ],
        'highlights': [
            'No build step: Django templates, deployed by copying files',
            'Purpose-built four-model panel instead of a generic CMS',
            'Four themes driven from a settings singleton',
            'Request-level access logging as a first-class feature',
        ],
    },
    {
        'slug': 'ezbookkeeping',
        'name': 'ezBookkeeping — budget fork',
        'tagline': 'Upstream tracked what I spent. I needed it to track what I had left.',
        'year': '2026',
        'status': 'live',
        'accent': '#38bdf8',
        'repo': 'ezbookkeeping',
        'repo_label': 'Rehd96/ezbookkeeping (fork)',
        'live_url': 'https://labustagialla.it/ezbk',
        'live_label': 'labustagialla.it/ezbk',
        'role': 'Fork maintainer — feature work in Go and Vue',
        'stack': ['Go', 'Vue 3', 'Vite', 'SQLite', 'Docker', 'GitHub Actions'],
        'summary': (
            'A fork of the self-hosted personal finance app ezBookkeeping, adding the '
            'feature it was missing for how I actually budget: monthly variable '
            'budgets, a weekly spending breakdown, and a pace card that tells me '
            'whether I am ahead or behind before the month ends.'
        ),
        'sections': [
            {
                'heading': 'Why fork it',
                'body': [
                    'ezBookkeeping is a genuinely good piece of software — one Go binary '
                    'serving a JSON API and a compiled Vue frontend, with SQLite, MySQL and '
                    'PostgreSQL behind the same abstraction. Self-hosted, so my financial '
                    'data stays on my machine.',
                    'What it did was record history accurately. What I wanted was the '
                    'forward-looking question: it is the 18th, I have spent this much, am I '
                    'going to make it to the end of the month? That is a different feature, '
                    'not a bug report.',
                ],
            },
            {
                'heading': 'What I added',
                'body': [
                    'Monthly variable budget tracking and a weekly spending breakdown on '
                    'the desktop home page, then a weekly budget pace card — the '
                    '"ahead or behind, right now" answer — and the matching budget and '
                    'spending views for mobile, because the moment you want that number is '
                    'while you are standing in a shop.',
                    'Working in a mature upstream codebase meant touching both halves: Go '
                    'services and API surface on one side, Vue 3 components on the other, '
                    'matching conventions I did not write.',
                    'Along the way: fixing stale upstream test failures, honouring a '
                    'NO_LINT build flag through the Docker frontend-builder stage, and a '
                    'GitHub Actions workflow that builds and pushes the feature image to '
                    'ghcr.io so the VPS can just pull it.',
                ],
            },
            {
                'heading': 'Where it stands',
                'body': [
                    'Running on my VPS as my day-to-day finance app, which is the only '
                    'test that matters for this one — the fork stays alive because I use it '
                    'every week.',
                ],
            },
        ],
        'highlights': [
            'Feature work across a Go backend and a Vue 3 frontend',
            'Weekly budget pace card: ahead or behind, at a glance',
            'Mobile budget and spending views',
            'CI pipeline publishing the fork image to ghcr.io',
        ],
    },
    {
        'slug': 'fainance-automation',
        'name': 'Fainance Automation',
        'tagline': 'The project I built to get the job I have.',
        'year': '2026',
        'status': 'archived',
        'accent': '#fb7185',
        'repo': 'Fainance_Automation',
        'live_url': None,
        'live_label': 'Archived — no longer deployed',
        'role': 'Sole developer',
        'stack': ['Node.js', 'Python', 'Apache Kafka', 'Redis', 'Socket.io',
                  'Claude Vision API', 'Docker Compose'],
        'summary': (
            'An event-driven Accounts Payable platform. Photograph an invoice with '
            'your phone; it is OCR\'d by a vision model, the fields come back for you '
            'to correct, and then it moves through a six-stage Kafka pipeline that '
            'validates it, matches it against known transactions and routes it to '
            'approved, rejected or escalated — with the whole journey streaming into '
            'the browser live.'
        ),
        'sections': [
            {
                'heading': 'Why it exists',
                'body': [
                    'I built this to demonstrate that I could design and ship an '
                    'event-driven system end to end, for a role in exactly that domain. It '
                    'worked: it is the project that got me my current job.',
                    'That also means it was always a portfolio piece rather than a product, '
                    'and I have retired it rather than pretend otherwise. The code and the '
                    'architecture are still worth reading, which is why it is still here.',
                ],
            },
            {
                'heading': 'The architecture',
                'body': [
                    'A Node.js backend owns the browser-facing edge: the upload endpoint, '
                    'Claude Vision OCR and field extraction, the confirmation step, a Redis '
                    'state store and a Socket.io channel pushing updates to the UI.',
                    'A Python producer owns the pipeline: six Kafka topics carrying an '
                    'invoice from raw through parsed or AI-enriched, then validated, '
                    'matched and finally to a decision. Readable invoices take the cheap '
                    'regex path; unreadable or low-confidence ones branch to the model. '
                    'Uploads that a human has already reviewed skip straight to validated, '
                    'so only matching and routing run.',
                    'Every invoice ends as approved, rejected with structured feedback, or '
                    'escalated for human review — high value, no matching transaction, an '
                    'amount discrepancy, or low match confidence. The targets were straight-'
                    'through processing above 60% and escalations under 15%.',
                ],
            },
            {
                'heading': 'What I took from it',
                'body': [
                    'The habits that stuck are all from here: designing around topics and '
                    'stages instead of function calls, treating "escalate to a human" as a '
                    'first-class outcome rather than an error path, and putting a review '
                    'step between a model\'s output and anything irreversible.',
                    'Every project on this page since has been shaped by that last one.',
                ],
            },
        ],
        'highlights': [
            'Six-topic Kafka pipeline with a branching enrichment path',
            'Vision-model OCR with a mandatory human review step',
            'Live pipeline state pushed to the browser over WebSocket',
            'Landed me my current job',
        ],
    },
    {
        'slug': 'rentwatch',
        'name': 'rentwatch',
        'tagline': 'Finding a flat in Turin without re-reading the same 300 listings every day.',
        'year': '2026',
        'status': 'active',
        'accent': '#facc15',
        'repo': 'rentwatch',
        'live_url': None,
        'live_label': 'Runs locally — self-host it yourself',
        'role': 'Sole developer',
        'stack': ['Python 3.11', 'curl_cffi', 'FastAPI', 'SQLite',
                  'Telegram Bot API'],
        'summary': (
            'A rental-market monitor for immobiliare.it. It scrapes a city\'s '
            'listings on a schedule, keeps every price change in SQLite, and shows a '
            'dashboard of €/m² by zone, days on market, price drops and what appeared '
            'since yesterday. Three dependencies, no framework, runs on a laptop.'
        ),
        'sections': [
            {
                'heading': 'The problem',
                'body': [
                    'Looking for a flat to rent in Turin means re-checking hundreds of '
                    'listings every day with no way to tell what is new, what has dropped '
                    'in price and what is already gone. The portal shows you the market; it '
                    'never shows you the difference since your last visit.',
                    'rentwatch does that reading and presents only the delta.',
                ],
            },
            {
                'heading': 'What it does',
                'body': [
                    'Price history: every change is recorded, so the dashboard shows how '
                    'far a listing has fallen from its original asking price — the single '
                    'best signal for what is actually negotiable.',
                    'Disappearances: a listing missing from a full scan is marked removed '
                    '(probably rented) but kept in the database, so you can see how fast '
                    'the good ones go.',
                    'Median €/m² per zone, a "new in the last 24 hours / 3 / 7 days" filter, '
                    'and dismiss (✕) and favourite (♥) actions — dismissed listings never '
                    'come back, favourites stay tracked even after they are pulled from the '
                    'portal.',
                    'A Markdown report regenerated on every scan for reading on a phone, '
                    'and optional Telegram notifications for new listings.',
                ],
            },
            {
                'heading': 'Two problems worth describing',
                'body': [
                    'Plain HTTP requests get a 403 — the portal fingerprints the TLS '
                    'handshake, not the user agent. The scraper uses curl_cffi impersonating '
                    'Chrome so the handshake matches the browser it claims to be.',
                    'And the data itself lies in a specific way: student agencies list a '
                    'single room as an apartment, with the per-person price and the whole '
                    'flat\'s floor area. A heuristic flags them — under €5/m², or rent per '
                    'room below €120 with four or more rooms — and pulls them out of the '
                    'medians so they cannot drag the market averages down. They are flagged, '
                    'never deleted: occasionally one is a genuine bargain.',
                    'The first scan deliberately sends no notifications. Otherwise it '
                    'announces the entire market at once.',
                ],
            },
            {
                'heading': 'Where it stands',
                'body': [
                    'Actively in use — it is currently how I am looking for a flat. It is '
                    'also the project I would point at to explain what I like building: a '
                    'small tool that removes a real, boring, daily task.',
                ],
            },
        ],
        'highlights': [
            'TLS fingerprint impersonation to get past a 403',
            'Full price history, not just current asking price',
            'Heuristic that flags mis-listed rooms and excludes them from medians',
            'Three dependencies total',
        ],
    },
]

BY_SLUG = {p['slug']: p for p in PROJECTS}


def enrich(project):
    """Add the derived fields templates want, without duplicating them above."""
    p = dict(project)
    label, css = STATUS[p['status']]
    p['status_label'] = label
    p['status_css'] = css
    p['repo_url'] = f'https://github.com/{GITHUB_USER}/{p["repo"]}'
    p.setdefault('repo_label', f'{GITHUB_USER}/{p["repo"]}')
    return p


def all_projects():
    return [enrich(p) for p in PROJECTS]


def get_project(slug):
    project = BY_SLUG.get(slug)
    return enrich(project) if project else None


def neighbours(slug):
    """(previous, next) for the footer pager — wraps around."""
    slugs = [p['slug'] for p in PROJECTS]
    if slug not in slugs:
        return None, None
    i = slugs.index(slug)
    return (enrich(PROJECTS[i - 1]),
            enrich(PROJECTS[(i + 1) % len(PROJECTS)]))
