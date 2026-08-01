# Deploying to labustagialla.it

The portfolio takes the **root** of the domain. The three existing subpaths keep
working untouched — nginx matches the more specific prefix first, so only
requests that fall through to `/` reach this app.

```
internet → nginx (host) ─┬─▶ /            ─▶ 127.0.0.1:8010  ← this app (gunicorn, systemd)
                         ├─▶ /static/     ─▶ served by nginx from staticfiles/
                         ├─▶ /cff/        ─▶ festival (docker)
                         ├─▶ /fai         ─▶ Fainance Automation
                         └─▶ /ezbk        ─▶ ezBookkeeping
```

> **Check first:** if something is already answering at `/` on labustagialla.it,
> this replaces it. `curl -sI https://labustagialla.it/` before you start, and
> keep whatever nginx block currently handles `/` in case you want it back.

## 1. Pick a free port

`8010` is the assumption throughout. Confirm nothing else has it — the festival
uses 3000/3001, writerblog 8000, ezBookkeeping 8080, the monitor 4000:

```bash
ss -tlnp | grep -E ':(8010|8000|8080|3000|3001|4000)\b'
```

## 2. Clone and set up

```bash
ssh vps
git clone git@github.com:Rehd96/HiImIon.git ~/HiImIon
cd ~/HiImIon

python3 -m venv venv
./venv/bin/pip install -r requirements.txt

cp .env.example .env
./venv/bin/python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
# paste that into DJANGO_SECRET_KEY, and set DJANGO_DEBUG=false
nano .env

set -a; . ./.env; set +a
./venv/bin/python manage.py migrate
./venv/bin/python manage.py collectstatic --noinput
./venv/bin/python manage.py createsuperuser      # your panel login
```

## 3. systemd

```bash
sudo cp deploy/hiimion.service /etc/systemd/system/hiimion.service
sudo systemctl daemon-reload
sudo systemctl enable --now hiimion
systemctl status hiimion --no-pager

curl -sI http://127.0.0.1:8010/ | head -1     # expect 200
```

If the unit fails to start: `sudo journalctl -u hiimion -n 50 --no-pager`. The
usual causes are a missing `.env`, a port collision, or `staticfiles/` not being
writable by the `ion` user.

## 4. nginx

Rate-limit zones go at `http{}` scope — add to `/etc/nginx/conf.d/ratelimits.conf`
(skip any that already exist there from the festival setup):

```nginx
limit_req_zone $binary_remote_addr zone=portfolio_login:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=portfolio_all:10m   rate=120r/m;
```

Then paste the location blocks from `deploy/nginx-labustagialla.conf` into the
existing `server { listen 443 ssl; server_name labustagialla.it; }` block —
**after** the `/cff`, `/fai` and `/ezbk` blocks.

```bash
sudo nginx -t && sudo systemctl reload nginx
```

Verify the neighbours survived:

```bash
for p in / /panel/login/ /cff/ /ezbk; do
  printf '%-16s %s\n' "$p" "$(curl -so /dev/null -w '%{http_code}' https://labustagialla.it$p)"
done
```

## 5. TLS

The existing Let's Encrypt certificate already covers `labustagialla.it`. If it
does not cover `www`:

```bash
sudo certbot --nginx -d labustagialla.it -d www.labustagialla.it
```

## 6. Retention cron

```bash
sudo crontab -e
```

```cron
17 4 * * * cd /home/ion/HiImIon && ./venv/bin/python manage.py prune_views >> /var/log/hiimion-prune.log 2>&1
```

## Updating

```bash
cd ~/HiImIon && ./deploy/deploy.sh
```

Pull, install, migrate, collectstatic, `check --deploy`, restart, smoke test.
Content-only changes are just an edit to `portfolio/projects.py` and a restart.

## Rollback

```bash
cd ~/HiImIon
git log --oneline -5
git checkout <previous-sha>
./deploy/deploy.sh
```

The database only holds page views, so rolling the code back is safe — no
content lives in it.

## Adding this to the monitor

`festival-monitor` watches the other four apps. To add this one, append to
`deploy/monitor-agent/agent-config.json` on the VPS:

```json
{ "name": "Portfolio", "url": "http://127.0.0.1:8010/", "expect": 200 }
```

then `sudo systemctl restart festival-monitor-agent`.
