# Repository Guidelines

## Project Structure & Module Organization

This is a Django 5.1 portfolio site with a private analytics panel and a kitten-adoption feature. Project configuration and root URLs live in `hiimion/`. The two Django apps are:

- `portfolio/`: public portfolio pages, project data in `projects.py`, analytics middleware/models, panel views, and the `prune_views` management command.
- `kitten/`: adoption pages, profile/post models, forms, and printable flyers.

HTML is grouped by responsibility in `templates/site/`, `templates/panel/`, and `templates/kitten/`. Keep CSS and image assets under `static/css/` and `static/img/`; committed migrations belong in each app’s `migrations/` directory. Deployment material is in `deploy/`, with operational notes in `DEPLOY.md` and `VPS_COMMANDS.txt`.

## Build, Test, and Development Commands

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt  # install Django and runtime packages
./venv/bin/python manage.py migrate          # apply local SQLite migrations
./venv/bin/python manage.py runserver        # serve http://127.0.0.1:8000
./venv/bin/python manage.py test             # run the full test suite
./venv/bin/python manage.py test portfolio   # run one app's tests
```

Run `./venv/bin/python manage.py makemigrations` after model changes and review the generated migration before committing. Production deployment uses `./deploy/deploy.sh`; follow `DEPLOY.md` rather than adapting production commands ad hoc.

## Coding Style & Naming Conventions

Follow existing Python conventions: four-space indentation, `snake_case` functions/variables, `PascalCase` models and test classes, and focused modules. Keep imports grouped like existing files. Use Django `reverse()` in tests and views when named URLs are available. Template and static filenames are lowercase and descriptive (for example, `templates/site/project.html` and `static/css/panel.css`).

Portfolio content is data, not database state: add or edit projects in `portfolio/projects.py`. Preserve its dict schema; slugs are lowercase, URL-safe identifiers. When adding a `screenshot`, include the asset in `static/` and meaningful `screenshot_alt` text.

## Testing Guidelines

Tests use Django's `TestCase` and live beside their app in `portfolio/tests.py` or `kitten/tests.py`. Name test methods `test_<behavior>` and cover normal, authorization, and failure paths. Add tests for new routes, model behavior, and analytics exclusions. Run the full suite before opening a PR; there is no separate coverage threshold configured.

## Commit & Pull Request Guidelines

Recent commits use concise, imperative summaries (for example, `Add /healthz for the VPS monitor`). Keep each commit narrowly scoped. PRs should state the user-visible change, list test commands run, link relevant issues, and include screenshots for template/CSS changes. Call out migrations, deployment changes, and any configuration or privacy impact explicitly.

## Security & Configuration

Never commit production secrets. Set `DJANGO_SECRET_KEY` and `DJANGO_DEBUG` through the environment; the default key is development-only. Treat collected `PageView` data as sensitive and preserve the middleware’s exclusions for static pages and `/panel/`.
