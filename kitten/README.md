# 🐾 Django App: `kitten`

Applicazione Django modulare per la gestione del feed multimediale, del profilo informativo e dei materiali promozionali per l'adozione del gattino (**Mais**).

---

## Struttura della Cartella

```
kitten/
├── __init__.py           # Configurazione app predefinita
├── admin.py              # Registrazione modelli per Django Admin
├── apps.py               # KittenConfig (verbose_name: 'Adozione Mais')
├── forms.py              # KittenProfileForm e KittenPostForm
├── migrations/           # Migrazioni dello schema del database
│   ├── 0001_initial.py
│   └── __init__.py
├── models.py             # KittenProfile e KittenPost
├── tests.py              # Suite di test unitari automatizzati
├── urls.py               # Rotte HTTP per pubblico, admin, QR e flyer
└── views.py              # Controller e logica di business
```

---

## Modelli Principali

### `KittenProfile`
Profilo descrittivo del gattino da adottare:
* `name` (CharField): Nome (default `'Mais'`).
* `slug` (SlugField): Slug per l'URL (default `'mais'`).
* `tagline` (CharField): Slogan riassuntivo.
* `age_text` (CharField): Età approssimativa (es. `'7 settimane circa'`).
* `gender` (CharField): Sesso (`'Femmina'` o `'Maschio'`).
* `color` (CharField): Caratteristiche del manto.
* `location` (CharField): Città e zona per l'incontro conoscitivo.
* `phone_number` (CharField): Numero per contatto telefonico e WhatsApp.
* `whatsapp_number` (CharField): Numero WhatsApp alternativo (opzionale).
* `contact_email` (EmailField): Indirizzo email opzionale.
* `bio_intro`, `personality`, `health_info`, `adoption_requirements` (TextField): Testi descrittivi.
* `cover_image` (ImageField): Foto principale del gattino.
* `is_adopted` (BooleanField): Flag di adozione avvenuta.
* `likes_count` (PositiveIntegerField): Numero di fusa/cuori ricevuti.

**Proprietà utili:**
* `clean_whatsapp_number`: Normalizza il numero togliendo spazi e formattando il prefisso per l'API WhatsApp.
* `whatsapp_url`: Link completo `https://wa.me/...` con testo di presentazione precompilato.
* `cover_url`: Restituisce l'URL dell'immagine o il fallback su `/static/img/mais_placeholder.jpg`.

### `KittenPost`
Post multimediale del feed/diario:
* `kitten` (ForeignKey): Collegamento al profilo.
* `title` (CharField): Titolo o breve intestazione.
* `caption` (TextField): Didascalia o aneddoto.
* `tag` (CharField): Categoria del momento (`gioco`, `pappa`, `coccole`, `nanna`, `scoperte`, `visita`, `altro`).
* `media_type` (CharField): Tipo di media (`photo`, `video`, `text`).
* `image` (ImageField): Upload immagine (`kitten/posts/images/`).
* `video` (FileField): Upload video (`kitten/posts/videos/`).
* `created_at` (DateTimeField): Data e ora del post.
* `likes` (PositiveIntegerField): Contatore cuori del singolo post.

---

## Endpoint e Routing (`kitten/urls.py`)

| URL | Nome rotta | Metodo | Accesso |
|---|---|---|---|
| `/mais/` | `kitten_detail` | `GET` | Pubblico |
| `/adotta/` | `kitten_adotta` | `GET` | Redirect 302 ➔ `/mais/` |
| `/gattino/` | `kitten_gattino` | `GET` | Redirect 302 ➔ `/mais/` |
| `/mais/like/` | `kitten_like` | `POST` | Pubblico (AJAX con CSRF) |
| `/mais/qr/` | `kitten_qr` | `GET` | Pubblico (restituisce PNG) |
| `/mais/volantino/a4/` | `kitten_flyer_a4` | `GET` | Pubblico |
| `/mais/volantino/a5/` | `kitten_flyer_a5` | `GET` | Pubblico |
| `/mais/gestione/` | `kitten_admin` | `GET`, `POST` | Staff Only (`is_staff`) |
| `/mais/post/<id>/delete/` | `kitten_delete_post` | `POST` | Staff Only (`is_staff`) |

---

## Comandi Utili

### Eseguire i test dell'app
```bash
./venv/bin/python manage.py test kitten
```

### Generare nuove migrazioni se si modificano i campi
```bash
./venv/bin/python manage.py makemigrations kitten
./venv/bin/python manage.py migrate
```
