# Lichtblick

Ein schlanker Social‑Prototype: **FastAPI**‑Backend mit **fastapi-users** (JWT‑Auth), **ImageKit** für Medien‑Uploads, **SQLAlchemy async** auf SQLite sowie ein **Streamlit**‑Frontend.

---

## Inhalt

- [Features](#features)
- [Architektur](#architektur)
- [Projektstruktur](#projektstruktur)
- [Voraussetzungen](#voraussetzungen)
- [Installation](#installation)
- [Umgebungsvariablen (.env)](#umgebungsvariablen-env)
- [Starten](#starten)
- [Nutzung](#nutzung)
- [API-Referenz](#api-referenz)
- [Datenbankmodell](#datenbankmodell)
- [Konfiguration](#konfiguration)
- [Troubleshooting](#troubleshooting)
- [Sicherheit & Secrets](#sicherheit--secrets)
- [Tests & manuelle Checks](#tests--manuelle-checks)
- [Deployment-Hinweise](#deployment-hinweise)
- [Git & GitHub](#git--github)
- [Roadmap](#roadmap)
- [Lizenz](#lizenz)

---

## Features

- **Auth** mit fastapi-users: Registrierung, Login (JWT), `GET /users/me`.
- **Uploads** von Bildern/Videos zu **ImageKit** inkl. URL‑Rückgabe.
- **Beiträge** in SQLite (`./test.db`) speichern und listen.
- **Kommentare** zu Beiträgen (Serverendpunkte vorhanden).
- **Likes/Dislikes** in der UI (fällt lokal zurück, falls Backend-Endpunkte fehlen).
- **Hell/Dunkel‑Modus** im Streamlit‑Frontend.

---

## Architektur

```
[Streamlit-Frontend]
        │  REST (JSON, JWT)
        ▼
[FastAPI + fastapi-users] ── SQLAlchemy (async) ──> [SQLite (test.db)]
        │
        └── ImageKit SDK ──> [ImageKit Storage/CDN]
```

- Das Frontend ruft die API mit JWT‑Bearer‑Token auf.
- Das Backend verwaltet Benutzer, speichert Beiträge/Kommentare in SQLite und lädt Medien zu ImageKit hoch.
- Medien werden **nicht** lokal gespeichert, sondern nur per URL referenziert.

---

## Projektstruktur

```
.
├─ backend/
│  ├─ api.py                 # FastAPI-Routen (Upload, Feed, Delete, Comments)
│  ├─ users.py               # fastapi-users Konfiguration (JWT, UserManager)
│  ├─ database.py            # SQLAlchemy-Modelle + async Engine/Session
│  ├─ schemas.py             # Pydantic-Schemas (User, Post)
│  └─ storage_imagekit.py    # ImageKit-Client (ENV-basiert)
├─ run_backend.py            # Uvicorn-Startskript: startet backend.api:app
├─ frontend_lichtblick_final.py  # Streamlit-Frontend
├─ .env                      # lokale Konfiguration/Secrets (nicht committen)
└─ README.md
```

> Hinweis: In `database.py` wird der PostgreSQL‑`UUID`‑Typ auch unter SQLite genutzt. Für eine Demo ok, in Produktion passend typisieren.

---

## Voraussetzungen

- Python **3.10+**
- Ein **ImageKit**‑Account (für `IMAGEKIT_*` Variablen)
- Optional **uv** (schnelles Python‑Tooling): <https://github.com/astral-sh/uv>  
  Alternativ: klassisches `venv` + `pip`

---

## Installation

### Variante A: mit `uv` (empfohlen)

```bash
# Im Projektordner
uv venv
# Shell aktivieren
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .\.venv\Scripts\Activate.ps1

# Pakete installieren
uv pip install fastapi "uvicorn[standard]" fastapi-users[sqlalchemy]   sqlalchemy aiosqlite python-dotenv imagekitio requests streamlit
```

### Variante B: klassisches venv/pip

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .\.venv\Scripts\Activate.ps1

pip install fastapi "uvicorn[standard]" fastapi-users[sqlalchemy]   sqlalchemy aiosqlite python-dotenv imagekitio requests streamlit
```

---

## Umgebungsvariablen (.env)

Lege im Projekt‑Root eine Datei **`.env`** an:

```env
IMAGEKIT_PRIVATE_KEY=private_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
IMAGEKIT_PUBLIC_KEY=public_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
IMAGEKIT_URL=https://ik.imagekit.io/<dein_path>

JWT_SECRET=ein_langer_zufallsstring
JWT_LIFETIME_SECONDS=3600

# optional fürs Frontend (Default: http://localhost:8000)
BACKEND_URL=http://localhost:8000
```

> **Wichtig:** `.env` **nicht** committen. Bei Leck sofort Schlüssel rotieren.

---

## Starten

### Backend

Variante 1: Startskript

```bash
python run_backend.py
# oder mit uv:
uv run python run_backend.py
```

Variante 2: direkt uvicorn

```bash
uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload
```

Beim Start werden die Tabellen per `create_db_and_tables()` in `./test.db` angelegt.

### Frontend

```bash
# BACKEND_URL kommt aus .env oder Default http://localhost:8000
streamlit run frontend_lichtblick_final.py
# oder mit uv:
uv run streamlit run frontend_lichtblick_final.py
```

Frontend öffnet sich typischerweise unter <http://localhost:8501>.

---

## Nutzung

1. **Registrieren**: Reiter „Registrieren“ (E‑Mail + Passwort).
2. **Anmelden**: Reiter „Anmelden“. Sidebar zeigt den eingeloggten Benutzer.
3. **Beiträge**: Tab „Beiträge“ listet neueste Posts (Besitzer kann löschen).
4. **Upload**: Tab „Beitrag erstellen“ → Datei wählen, optional Beschreibung → „Teilen“.
5. **Kommentare**: Unter jedem Beitrag anzeigen/erstellen.
6. **Likes/Dislikes**: Buttons pro Beitrag.  
   *Wenn das Backend die Endpunkte nicht anbietet, reagiert nur die UI lokal.*

---

## API-Referenz

### Auth (fastapi-users)

- `POST /auth/jwt/login`  
  **Form-Body:** `username=<email>&password=<pass>` → `{ "access_token": "..." }`

- `POST /auth/register`  
  **JSON:** `{ "email": "...", "password": "..." }` → `201 Created`

- `GET /users/me`  
  **Header:** `Authorization: Bearer <token>` → User‑Objekt

### Beiträge & Upload

- `POST /upload`  
  **Multipart:** `file` (Datei), **Form:** `caption` (Text).  
  Lädt Datei zu ImageKit, speichert Post in DB. Rückgabe: Post‑Objekt.

- `GET /feed`  
  Liefert Liste von Posts, absteigend nach `created_at`. Felder u. a.:  
  `id`, `user_id`, `caption`, `url`, `file_type`, `created_at`, `is_owner`, `email`

- `DELETE /post/{post_id}`  
  Löscht Post, nur wenn `current_active_user` der Besitzer ist.

### Kommentare

- `GET /post/{post_id}/comments`  
  Antwort: `{ "comments": [ { "id", "post_id", "user_id", "text", "created_at", "author" }, ... ] }`

- `POST /post/{post_id}/comments`  
  **JSON:** `{ "text": "..." }` → `{ "ok": true, "id": "<uuid>" }`

> Likes/Dislikes: Frontend erwartet optional  
> `POST /post/{id}/like`, `/unlike`, `/dislike`, `/undislike`.  
> Wenn nicht vorhanden, fällt die UI lokal zurück.

### Beispiel mit `curl`

```bash
# Login
curl -X POST http://localhost:8000/auth/jwt/login   -H "Content-Type: application/x-www-form-urlencoded"   -d "username=user@example.com&password=secret"

# Feed abrufen
curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/feed

# Kommentar hinzufügen
curl -X POST http://localhost:8000/post/<POST_ID>/comments   -H "Authorization: Bearer <TOKEN>"   -H "Content-Type: application/json"   -d '{"text":"Schöner Beitrag!"}'
```

---

## Datenbankmodell

**User** (von fastapi-users)  
- `id` (UUID, PK), `email`, `hashed_password`, `is_active`, `is_superuser`, `is_verified`

**Post**  
- `id` (UUID, PK)  
- `user_id` (UUID, FK → User.id)  
- `caption` (Text)  
- `url` (String, öffentlich)  
- `file_type` (String, z. B. "image" / "video" oder MIME)  
- `file_name` (String)  
- `created_at` (DateTime, UTC)  
- Beziehungen: `user` (n:1), `comments` (1:n)

**Comment**  
- `id` (UUID, PK)  
- `post_id` (UUID, FK → Post.id)  
- `user_id` (UUID, FK → User.id)  
- `text` (Text)  
- `created_at` (DateTime, UTC)

> In der Demo ist `Comment` im Code an einer Stelle innerhalb der `Post`‑Klasse definiert. Für produktiven Einsatz empfiehlt sich eine Top‑Level‑Definition.

---

## Konfiguration

- **DB‑Pfad**: `backend/database.py` → `DATABASE_URL = "sqlite+aiosqlite:///./test.db"`  
  Für Produktion: ENV nutzen oder Postgres einrichten.
- **ImageKit**: `storage_imagekit.py` liest `IMAGEKIT_*` aus `.env`.
- **CORS**: Bei abweichenden Hosts/Ports ggf. `CORSMiddleware` ergänzen.
- **JWT**: `JWT_SECRET` sicher halten und regelmäßig rotieren.

---

## Troubleshooting

- **`no module named app`**  
  Imports/Startpfade korrigieren. Start über `run_backend.py` oder `uvicorn backend.api:app`.

- **Streamlit Warnung „use_column_width deprecated“**  
  Frontend nutzt `use_container_width=True` (berücksichtigt).

- **SessionState-Fehler beim Kommentieren**  
  Kommentare werden in einem `st.form(..., clear_on_submit=True)` gepostet → behoben.

- **Uploads schlagen fehl**  
  `.env` prüfen (`IMAGEKIT_*` und korrekter `IMAGEKIT_URL`‑Endpoint).

- **Kommentare verschwinden nach Reload**  
  Sicherstellen, dass Kommentar‑Endpunkte aktiv sind und Tabelle existiert. Sonst fällt UI lokal zurück.

- **Dark‑Mode schaltet nicht**  
  Browser‑Cache leeren oder Seite neu laden. CSS‑Variablen werden dynamisch gesetzt.

---

## Sicherheit & Secrets

- `.env` niemals committen.  
- ImageKit‑Schlüssel bei Leck **sofort** rotieren.  
- In Produktion HTTPS erzwingen, starke Passwörter verlangen, Session‑/Rate‑Limits erwägen.

---

## Tests & manuelle Checks

Schneller Smoke‑Test:

1. Backend starten → Log ohne Fehler.
2. Frontend starten → Registrieren → Anmelden.
3. Bild hochladen → Beitrag erscheint.
4. Kommentar hinzufügen → Seite neu laden → Kommentar bleibt.
5. Beitrag als Besitzer löschen → Eintrag verschwindet.

Optional automatisieren (PyTest) und HTTP‑Tests (HTTPie) ergänzen.

---

## Deployment-Hinweise

- Produktion: `reload=False`, Prozessmanager oder Gunicorn+Uvicorn‑Worker hinter Nginx/Caddy.
- Datenbank: Für Last oder mehrere Instanzen auf **PostgreSQL** wechseln.
- Statisches Caching/CDN für Medien übernimmt ImageKit.

---

## Git & GitHub

**.gitignore** (Beispiel):

```
.venv/
__pycache__/
*.pyc
.env
*.db
.streamlit/
```

Initialer Push:

```bash
git init
git add .
git commit -m "Initial commit: Lichtblick"
git branch -M main
git remote add origin <dein-repo-url>
git push -u origin main
```

---

## Roadmap

- Persistente Likes/Dislikes im Backend
- Paging/Filter, Suche
- Alternativer Storage (S3 kompatibel)
- Rollen/Rechte, Moderation
- Tests (PyTest) und CI

---

## Lizenz

Wähle eine Lizenz und füge sie als `LICENSE` hinzu (z. B. MIT).
