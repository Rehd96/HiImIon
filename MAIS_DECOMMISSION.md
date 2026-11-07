# Decommissioning: Progetto Adozione Mais 🐾

Questo documento riassume tutte le operazioni effettuate per la dismissione completa della sezione web, del pannello di gestione e degli asset relativi all'adozione della gattina **Mais**, in seguito all'avvenuta adozione.

---

## 1. Architettura e Identificazione del Componente

Inizialmente era stato ipotizzato che il servizio potesse trovarsi all'interno di un container Docker isolato. L'analisi dell'infrastruttura ha evidenziato che:
- La gestione e le pagine di Mais non erano ospitate in un container separato, bensì all'interno dell'applicazione Django **`kitten`** integrata nel progetto principale **`HiImIon`** (`https://labustagialla.it`), servito via Gunicorn (`hiimion.service` su porta locale `8010`) e reverse-proxied da Nginx.
- Gli endpoint coinvolti erano:
  - `/mais/` (landing pubblica e feed fotografico/video)
  - `/mais/gestione/` (pannello di amministrazione e chat per il custode)
  - `/mais/like/` (endpoint AJAX fusa/cuori)
  - `/mais/qr/` (generazione dinamica QR code)
  - `/mais/volantino/a4/` e `/mais/volantino/a5/` (locandine stampabili)
  - `/mais/api/...` (beacon analitici cookieless e chat)
  - `/adotta/` e `/gattino/` (redirect amichevoli verso `/mais/`)

---

## 2. Operazioni Eseguite nel Codice

1. **Disattivazione delle Route URL**:
   - Rimosso `path('', include('kitten.urls'))` da `hiimion/urls.py`.
   - Rimosso il mapping globale per i media di sviluppo (`re_path(r'^media/...', serve)`).
   - Tutte le richieste verso `/mais/*`, `/adotta/`, `/gattino/` e `/media/*` restituiscono ora **404 Not Found**.

2. **Disattivazione dell'Applicazione in Django**:
   - Rimosso `'kitten'` da `INSTALLED_APPS` in `hiimion/settings.py`.
   - Il database SQLite mantiene integre le tabelle e lo storico a livello di file, ma l'applicazione è completamente esclusa dal runtime Django.

3. **Pulizia del Pannello Staff (/panel/)**:
   - Rimossi i pulsanti di navigazione `🐾 Mais` e `🐾 Torna a Mais (/mais/) ↗` da `templates/panel/base.html`.
   - Rimossa la logica di redirect al logout per Mais da `portfolio/panel_views.py`.

4. **Rimozione dei File e Asset Dismessi**:
   - Rimossa la cartella applicativa `kitten/` (modelli, viste, form, admin, fixture, migrazioni e test).
   - Rimossi i template dedicati `templates/kitten/` (`admin.html`, `detail.html`, `flyer_a4.html`, `flyer_a5.html`).
   - Rimossi gli stili CSS e immagini statiche `static/css/kitten.css`, `static/css/flyer.css`, `static/img/mais_placeholder.jpg`.
   - Rimossi i file di documentazione e materiale correlato (`KITTEN_ADOPTION.md`, `locandina_mais_a4.pdf`).
   - Aggiornati `README.md` e `AGENTS.md` per riflettere lo stato attuale del repository (solo app `portfolio`).

---

## 3. Deployment sul Server di Produzione (VPS)

1. I commit sono stati caricati sul ramo `main` su GitHub.
2. Sul server di produzione (`217.154.23.127`):
   - Eseguito `git pull --ff-only`.
   - Eseguito `python manage.py collectstatic --noinput` per aggiornare il manifest degli statici.
   - Eseguiti i test di regressione del portafoglio (27/27 test superati).
   - Riavviato il servizio systemd `hiimion.service`.
   - Eliminati dal filesystem del server i file media obsoleti in `/root/HiImIon/media/kitten/`.

---

## 4. Verifica di Sicurezza e Risultati HTTP

I controlli su `https://labustagialla.it` hanno confermato lo spegnimento degli endpoint di Mais e l'integrità del resto della piattaforma:

| Endpoint | Esito Atteso | Esito Rilevato | Stato |
| :--- | :--- | :--- | :--- |
| `https://labustagialla.it/mais/gestione/` | 404 Not Found | **404** | ✅ Spento |
| `https://labustagialla.it/mais/` | 404 Not Found | **404** | ✅ Spento |
| `https://labustagialla.it/adotta/` | 404 Not Found | **404** | ✅ Spento |
| `https://labustagialla.it/gattino/` | 404 Not Found | **404** | ✅ Spento |
| `https://labustagialla.it/media/kitten/...` | 404 Not Found | **404** | ✅ Spento |
| `https://labustagialla.it/` | 200 OK | **200** | ✅ Attivo |
| `https://labustagialla.it/panel/login/` | 200 OK | **200** | ✅ Attivo |
| `https://labustagialla.it/healthz` | 200 OK | **200** | ✅ Attivo |
| `https://labustagialla.it/blog/` | 200 OK | **200** | ✅ Attivo |
| `https://labustagialla.it/ezbk/` | 200 OK | **200** | ✅ Attivo |

---

## 5. Audit di Sicurezza degli Endpoint e Protezione Informazioni

È stata condotta una scansione completa di probing sugli endpoint per scongiurare qualsiasi fuga di file di configurazione, repository, database o file istruzioni per agenti/AI (`AGENTS.md` e simili):

| Categoria | Percorso Verificato | Codice HTTP | Note di Sicurezza |
| :--- | :--- | :--- | :--- |
| **Agent / AI Files** | `/AGENTS.md`, `/agents.md`, `/.agents/` | **404** | Non instradati, nessun file servito dal server web |
| **Git & Version Control** | `/.git/`, `/.git/config`, `/.git/HEAD` | **404** | Repository `.git` non accessibile |
| **Ambiente & Segreti** | `/.env`, `/.env.example`, `/.env.prod` | **404** | Variabili d'ambiente e chiavi protette |
| **Database & Backup** | `/db.sqlite3`, `/backup.sql`, `*.tar.gz` | **404** | File di database e backup inaccessibili via web |
| **Note & Docs Deploy** | `/DEPLOY.md`, `/VPS_COMMANDS.txt`, `/README.md` | **404** | File operativi e istruzioni non esposti |
| **Sorgenti Python** | `/manage.py`, `/requirements.txt`, `/hiimion/settings.py` | **404** | Nessun file sorgente o configurazione servito |
| **Pannello Django Admin** | `/django-admin/`, `/blog/django-admin/` | **403** | Bloccato a livello Nginx (`allow 127.0.0.1; deny all;`) |
| **Pannello Analytics** | `/panel/`, `/panel/views/` | **302** | Reindirizzamento a login obbligatorio (`/panel/login/`) |
| **Directory Traversal** | `/static/../.env`, `/static/%2e%2e/AGENTS.md` | **404** | Protezione attiva da WhiteNoise / Django |
| **Security Headers** | `X-Frame-Options`, `X-Content-Type-Options` | Presenti | Clickjacking e MIME sniffing bloccati |
| **Server Token** | `Server` header | **nginx** | Versione OS / Nginx mascherata (`server_tokens off;`) |
| **Rate Limiting** | Zone `wb_global` e `wb_auth` | **Attivo** | Protezione attiva contro brute-force e scraping (429) |

