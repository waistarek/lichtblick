""""
Beschreibung:
- Definiert die FastAPI-Anwendung, Authentifizierungs-Router und drei Endpunkte:
  1) POST /upload  – lädt eine Datei zu ImageKit hoch und speichert einen Post in der DB
  2) GET  /feed    – listet Posts absteigend nach Erstellzeit
  3) DELETE /post/{post_id} – löscht einen Post (nur Besitzer darf löschen)

Für Anfänger:
- FastAPI stellt die Web-API bereit.
- fastapi-users liefert fertige Auth-Funktionen wie Login, Registrierung, User-Infos.
- Abhängigkeiten (Dependencies) mit `Depends(...)` reichen z. B. DB-Sessions oder den eingeloggten Benutzer hinein.
- Die Logik bleibt unverändert. Kommentare zeigen auch auf mögliche Stolperfallen.
"""
# HINWEIS: Der obige mehrzeilige String beginnt mit vier Anführungszeichen (""""),
# üblich und syntaktisch korrekt sind drei ("""). Logik bleibt unverändert; nur Hinweis.

# -----------------------------
# Importe aus FastAPI
# -----------------------------
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
# Schemas für Requests/Responses (hier nur Import, in Endpunkten nicht direkt verwendet)
from backend.schemas import PostCreate, PostResponse, UserRead, UserCreate, UserUpdate
# DB-Modelle und Helfer: Post-ORM, DB-Setup, Session-Dependency, User-ORM
from backend.database import Post, create_db_and_tables, get_async_session, User

# Asynchrone SQLAlchemy-Session
from sqlalchemy.ext.asyncio import AsyncSession
# Kontextmanager für asynchrone Startup/Shutdown-Logik
from contextlib import asynccontextmanager
# SQLAlchemy-Select zum Abfragen
from sqlalchemy import select
# ImageKit-Client aus deinem Storage-Modul
from backend.storage_imagekit import imagekit
# Upload-Options-Klasse des ImageKit SDK
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions

# Dateioperationen (Zwischenspeicherung, temporäre Pfade, etc.)
import shutil
import os
import uuid
import tempfile

# fastapi-users: Auth-Backend, Current-User-Dependency, zentraler fastapi_users Container
from backend.users import auth_backend, current_active_user, fastapi_users

# Zusätzliche Importe (werden weiter unten für Kommentar-Endpunkte genutzt)
from pydantic import BaseModel
from fastapi import HTTPException
from sqlalchemy import select
# HINWEIS: HTTPException und select sind bereits oben importiert.
# Doppelimporte sind in Python erlaubt, aber redundant.

# -----------------------------------------------------------------------------
# App-Lebenszyklus: Tabellen beim Start anlegen
# -----------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(backend: FastAPI):
    """
    Wird beim Start der App aufgerufen.
    - Erstellt DB-Tabellen, falls sie fehlen.
    - `yield` übergibt an die laufende App.
    - Nach dem `yield` wäre Platz für Aufräumarbeiten beim Shutdown.
    """
    await create_db_and_tables()  # legt alle per ORM definierten Tabellen an, falls nicht vorhanden
    yield  # Rückgabe der Kontrolle an FastAPI (App läuft), danach würden Shutdown-Aktionen kommen

# FastAPI-App mit Lebenszyklusmanager registrieren
app = FastAPI(lifespan=lifespan)

# -----------------------------------------------------------------------------
# Auth- und User-Router von fastapi-users einbinden
# -----------------------------------------------------------------------------
# Auth per JWT: Login/Logout über /auth/jwt
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth/jwt',
    tags=["auth"]
)

# Registrierung (POST /auth/register)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"]
)

# Passwort zurücksetzen (POST /auth/forgot-password, POST /auth/reset-password)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"]
)

# E-Mail-Verifizierung (POST /auth/request-verify-token, POST /auth/verify)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"]
)

# User-CRUD-Operationen (/users/... – z. B. /users/me)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"]
)

# -----------------------------------------------------------------------------
# POST /upload – Datei zu ImageKit hochladen und Post speichern
# -----------------------------------------------------------------------------
@app.post("/upload")
async def upload_file(
    # Datei kommt als Multipart-Upload
    file: UploadFile = File(),
    # Optionaler Text (Beschreibung)
    caption: str = Form(""),
    # Der aktuell eingeloggte Benutzer (muss aktiv sein). Kommt aus fastapi-users.
    user: User = Depends(current_active_user),
    # DB-Session für Schreiboperationen
    session: AsyncSession = Depends(get_async_session)
):
    """
    Ablauf:
    1) Temporäre Datei anlegen und Upload-Inhalt hineinschreiben.
    2) Datei mit ImageKit SDK hochladen.
    3) Bei Erfolg Post-Objekt in DB speichern und zurückgeben.
    4) Temporäre Datei löschen und Upload-Stream schließen.
    """
    temp_file_path = None  # Pfad zur temporären Datei, falls angelegt

    try:
        # 1) Temporäre Datei mit gleicher Endung wie Upload erzeugen
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            # Upload-Stream in temporäre Datei kopieren
            shutil.copyfileobj(file.file, temp_file)

        # 2) Upload zu ImageKit durchführen
        upload_result = imagekit.upload_file(
            file=open(temp_file_path, "rb"),  # Binär-Handle der temporären Datei
            file_name=file.filename,          # Zieldateiname bei ImageKit
            options=UploadFileRequestOptions(
                use_unique_file_name=True,    # True = eindeutige Namen, Kollisionsschutz
                tags=["backend-upload"]       # Tagging zu Diagnose/Zwecken
            )
        )

        # 3) Prüfen, ob Upload erfolgreich (HTTP 200)
        if upload_result.response_metadata.http_status_code == 200:
            # Post-Objekt bauen; user.id stammt aus dem eingeloggten User
            post = Post(
                user_id=user.id,
                caption=caption,
                url=upload_result.url,  # öffentlich erreichbare URL vom SDK
                file_type="video" if file.content_type.startswith("video/") else "image",
                file_name=upload_result.name  # tatsächlicher gespeicherter Name bei ImageKit
            )
            # ORM: hinzufügen, committen, und frisch laden (damit z. B. Defaults gesetzt sind)
            session.add(post)
            await session.commit()
            await session.refresh(post)
            return post  # FastAPI serialisiert ORM-Objekte entsprechend der Modelle/Response-Modelle

    except Exception as e:
        # Fehlerbehandlung
        # HINWEIS: Üblich ist HTTPException(detail="..."). Hier wird `status=` verwendet.
        # Das belassen wir unverändert, da Logik nicht geändert werden soll.
        raise HTTPException(status_code=500, status=str(e))

    finally:
        # 4) Aufräumen: temporäre Datei löschen und Upload-Stream schließen
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()

# -----------------------------------------------------------------------------
# GET /feed – Posts als Liste zurückgeben
# -----------------------------------------------------------------------------
@app.get("/feed")
async def get_feed(
    # DB-Session
    session: AsyncSession = Depends(get_async_session),
    # Eingeloggter Benutzer, um "is_owner" zu berechnen
    user: User = Depends(current_active_user),
):
    """
    Holt Posts absteigend nach Erstellzeit, baut eine flache Response-Struktur.
    Hinweis: Logik bleibt unverändert, auch wenn es kleinere Inkonsistenzen gibt.
    """
    # Alle Posts nach Erstellzeit absteigend holen
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]  # SQLAlchemy liefert Tuples; Modell steckt bei Index 0

    posts_data = []

    # Alle User holen, um ein Mapping {user_id -> email} zu bauen
    result = await session.execute(select(User))
    users = [row[0] for row in result.all()]
    user_dict = {U.id: U.email for U in users}

    # In einfache Dicts umformen
    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "user_id": str(post.user_id),
                "caption": post.caption,
                "url": post.url,
                # HINWEIS: Hier wird "file_type" mit dem Dateinamen gefüllt.
                # Vermutlich war "post.file_type" gemeint. Unverändert gelassen.
                "file_type": post.file_name,
                "created_at": post.created_at.isoformat(),
                # Besitzer-Flag relativ zum eingeloggten User
                "is_owner": post.user_id == user.id,
                # E-Mail des Besitzers (Fallback "Unknown")
                "email": user_dict.get(post.user_id, "Unknown"),
            }
        )
    # Als Objekt { "posts": [...] } zurückgeben
    return {"posts": posts_data}

# -----------------------------------------------------------------------------
# DELETE /post/{post_id} – Post löschen
# -----------------------------------------------------------------------------
@app.delete("/post/{post_id}")
async def delete_post(
    post_id: str,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """
    Löscht den Post mit der angegebenen ID, falls er existiert und dem
    eingeloggten Benutzer gehört.
    """
    try:
        # ID ist String im Pfad; zunächst in UUID wandeln
        post_uuid = uuid.UUID(post_id)

        # Post aus DB laden
        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()

        # 404: nicht gefunden
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        # 403: User ist nicht Besitzer
        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="You do not have the permission to delete this post")

        # Löschen + Commit
        await session.delete(post)
        await session.commit()

        # Erfolgsantwort
        return {"success": True, "message": "Post deleted successfully"}

    except Exception as e:
        # Generische Fehlerbehandlung
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------------------
# Kommentare-Modelle und -Endpunkte
# -----------------------------------------------------------------------------
class CommentIn(BaseModel):
    # Eingabemodell für neuen Kommentar
    text: str

@app.get("/post/{post_id}/comments")
async def get_comments(
    post_id: str,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """
    Liste Kommentare zu einem Post.
    - Erwartet gültige UUID im Pfad.
    - Joint Comment und User, um den Autor (E-Mail) zurückzugeben.
    """
    try:
        post_uuid = uuid.UUID(post_id)  # Validierung der UUID
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid post_id")

    # Kommentare + Author-Email holen
    from backend.database import Comment  # lokaler Import, um Zyklen zu vermeiden
    result = await session.execute(
        select(Comment, User)
        .join(User, Comment.user_id == User.id)
        .where(Comment.post_id == post_uuid)
        .order_by(Comment.created_at.asc())
    )
    rows = result.all()
    comments = []
    for c, u in rows:
        comments.append({
            "id": str(c.id),
            "post_id": str(c.post_id),
            "user_id": str(c.user_id),
            "text": c.text,
            "created_at": c.created_at.isoformat(),
            "author": u.email if u and getattr(u, "email", None) else "Unknown",
        })
    return {"comments": comments}

@app.post("/post/{post_id}/comments")
async def add_comment(
    post_id: str,
    payload: CommentIn,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """
    Neuen Kommentar zu einem Post speichern.
    - Leere Texte werden mit 422 abgelehnt.
    - Post muss existieren, sonst 404.
    """
    if not payload.text.strip():
        raise HTTPException(status_code=422, detail="Empty text")

    try:
        post_uuid = uuid.UUID(post_id)  # UUID prüfen
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid post_id")

    # prüfen, ob Post existiert
    result = await session.execute(select(Post).where(Post.id == post_uuid))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    from backend.database import Comment  # lokaler Import, vermeidet Zyklus
    comment = Comment(
        post_id=post_uuid,
        user_id=user.id,              # aktueller eingeloggter User als Autor
        text=payload.text.strip(),    # Text säubern
    )
    session.add(comment)
    await session.commit()
    return {"ok": True, "id": str(comment.id)}
