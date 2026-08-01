#!/usr/bin/env bash
# Deploy the portfolio on the VPS. Idempotent — safe to re-run.
#
#   ssh vps
#   cd ~/HiImIon && ./deploy/deploy.sh
set -euo pipefail

cd "$(dirname "$0")/.."
ROOT="$PWD"

echo "→ Pulling latest"
git pull --ff-only

echo "→ Installing dependencies"
[ -d venv ] || python3 -m venv venv
./venv/bin/pip install -q --upgrade pip
./venv/bin/pip install -q -r requirements.txt

if [ ! -f .env ]; then
    echo "!! No .env — copy .env.example and fill in DJANGO_SECRET_KEY first." >&2
    exit 1
fi

# shellcheck disable=SC1091
set -a; . ./.env; set +a

echo "→ Migrating database"
./venv/bin/python manage.py migrate --noinput

echo "→ Collecting static files"
./venv/bin/python manage.py collectstatic --noinput

echo "→ Checking deployment settings"
./venv/bin/python manage.py check --deploy --fail-level ERROR

echo "→ Restarting service"
sudo systemctl restart hiimion
sleep 2
systemctl is-active --quiet hiimion || { sudo journalctl -u hiimion -n 30 --no-pager; exit 1; }

echo "→ Smoke test"
curl -fsS -o /dev/null -w '   / → %{http_code}\n' http://127.0.0.1:8010/
curl -fsS -o /dev/null -w '   /panel/login/ → %{http_code}\n' http://127.0.0.1:8010/panel/login/

echo "✓ Deployed from $ROOT"
