""""
Beschreibung:
- Definiert das Datenbank-Setup mit SQLAlchemy (asynchron) und die Tabellen `User` und `Post`.
- Stellt Session-/DB-Dependencies für FastAPI bereit (u. a. für fastapi-users).

Für Anfänger:
- Eine "Engine" ist die DB-Verbindung.
- Eine "Session" ist eine Arbeitseinheit für DB-Operationen.
- "Modelle" (ORM-Klassen) spiegeln Tabellen in Python wider.
- Diese Datei benutzt eine asynchrone Engine und Sessions (await erforderlich).

Hinweis:
- Die Variable DATABASE_URL zeigt auf eine SQLite-Datei `./test.db`.
- Es wird der PostgreSQL-spezifische UUID-Typ importiert und als Spaltentyp verwendet.
  Das ist für SQLite ungewöhnlich. Wir ändern die Logik hier bewusst nicht, benennen es
  nur. In echter Produktion würde man den passenden Typ pro DB wählen.
"""
# HINWEIS: Der obige mehrzeilige String beginnt mit vier Anführungszeichen ("""").
# Das ist in Python syntaktisch ungewöhnlich; üblich sind drei ("""). Hier wird NICHTS geändert,
# nur kommentiert. Der Code läuft, weil Python die erste öffnende Folge bis zur nächsten
# passenden schließenden Folge interpretiert. Behalte das exakt so bei, wenn du die Anweisung
# „nichts daran ändern“ strikt befolgst.

# Typ für asynchrone Generator-Dependencies (yield in async-Funktionen)
from collections.abc import AsyncGenerator

# UUID (Universally Unique Identifier – universell eindeutiger Bezeichner)
import uuid

# SQLAlchemy Kernbestandteile zum Definieren von Spalten und Beziehungen
from sqlalchemy import Column, String, Text, DateTime, ForeignKey

# PostgreSQL-spezifischer UUID-Spaltentyp.
# Achtung: Für SQLite ist dieser Typ nicht nativ. Hier NICHT geändert, nur kommentiert.
from sqlalchemy.dialects.postgresql import UUID

# Asynchrone Engine/Session und Sessionfabrik
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Basisklasse für ORM-Modelle und Relationship-Hilfen
from sqlalchemy.orm import DeclarativeBase, relationship

# Zeitstempel
from datetime import datetime

# fastapi-users DB-Hilfsklassen:
# - SQLAlchemyUserDatabase: Adapter für User-Datenbankzugriff
# - SQLAlchemyBaseUserTableUUID: liefert die User-Tabelle mit UUID-Primärschlüssel
from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID

# FastAPI Dependency-Injektion (Depends)
from fastapi import Depends

# -----------------------------------------------------------------------------
# DB-Verbindungs-URL
# -----------------------------------------------------------------------------
# SQLite (aiosqlite Treiber) mit Datei im Projekt-Root.
# In Produktion üblicherweise via ENV (Environment Variable) konfiguriert.
DATABASE_URL = "sqlite+aiosqlite:///./test.db"


# -----------------------------------------------------------------------------
# ORM-Basis und Modelle
# -----------------------------------------------------------------------------
class Base(DeclarativeBase):
    """Gemeinsame Basisklasse für alle ORM-Modelle. Enthält die Metadaten."""
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    """
    User-Tabelle, bereitgestellt durch fastapi-users Basisklasse.
    - Primärschlüssel: UUID
    - Standardspalten: id, email, hashed_password, is_active, is_superuser, is_verified

    Beziehung:
    - `posts`: 1:n Beziehung auf Post (ein Benutzer besitzt viele Posts)
    """
    posts = relationship("Post", back_populates="user")


class Post(Base):
    """
    Post-Tabelle für einfache Social-Posts.

    Spalten:
    - id: UUID Primärschlüssel (hier Postgres-UUID-Typ importiert; bei SQLite nicht nativ)
    - user_id: Fremdschlüssel auf User.id
    - caption: Beschreibungstext
    - url: öffentliche URL des hochgeladenen Inhalts (z. B. von ImageKit)
    - file_type: MIME-Typ oder Dateitypangabe (z. B. "image/jpeg")
    - file_name: Originaldateiname
    - created_at: Erstellungszeitpunkt (UTC)
    """
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)                  # UUID PK
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)            # FK -> User
    caption = Column(Text)                                                                  # Beschreibung
    url = Column(String, nullable=False)                                                    # öffentlich erreichbare URL
    file_type = Column(String, nullable=False)                                              # MIME/Typ
    file_name = Column(String, nullable=False)                                              # Dateiname
    created_at = Column(DateTime, default=datetime.utcnow)                                  # Zeitstempel

    # Beziehung zurück zum Besitzer (User). Muss zu User.posts passen.
    user = relationship("User", back_populates="posts")

    # NEU: Kommentare zu diesem Post (1:n). Cascade sorgt dafür, dass Kommentare mit gelöscht werden,
    # wenn der Post gelöscht wird.
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

    # HINWEIS WICHTIG:
    # Die folgende Klasse `Comment` ist INNERHALB von `Post` definiert. Das ist für SQLAlchemy unüblich.
    # Normalerweise definiert man Modelle auf Top-Level. String-Referenzen wie "Comment" in relationship()
    # lösen Namen global auf, nicht innerhalb der umschließenden Klasse. Das kann zu Mapping-Problemen führen.
    # Die Anweisung lautet jedoch „nichts daran ändern“. Daher bleibt es so, nur der Hinweis hier.
    class Comment(Base):
        __tablename__ = "comments"
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False)
        user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
        text = Column(Text, nullable=False)
        created_at = Column(DateTime, default=datetime.utcnow)

        # Beziehungen: Kommentar gehört zu genau einem Post und einem User.
        post = relationship("Post", back_populates="comments")
        user = relationship("User")


# -----------------------------------------------------------------------------
# Engine und Session-Fabrik (asynchron)
# -----------------------------------------------------------------------------
# Engine: hält die Verbindung zur Datenbank (hier: SQLite über aiosqlite).
engine = create_async_engine(DATABASE_URL)

# Session-Fabrik: erzeugt AsyncSession-Objekte.
# expire_on_commit=False verhindert, dass geladene Objekte nach Commit „vergessen“ werden.
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


# -----------------------------------------------------------------------------
# Lifecycle-Hilfen und Dependencies
# -----------------------------------------------------------------------------
async def create_db_and_tables():
    """
    Erzeugt alle Tabellen, die durch ORM-Modelle definiert sind.
    - Wird typischerweise beim App-Startup einmalig aufgerufen.
    - Nutzen von `run_sync`, weil create_all synchron ist, aber wir uns in async befinden.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency: liefert eine AsyncSession, die nach Verwendung sauber geschlossen wird.

    Verwendung in FastAPI-Endpunkten:
        async def route(session: AsyncSession = Depends(get_async_session)):
            ...
    """
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """
    Dependency für fastapi-users:
    - Liefert ein SQLAlchemyUserDatabase-Objekt, das CRUD auf der User-Tabelle kapselt.
    - fastapi-users erwartet genau diese Abstraktion für User-Operationen.
    """
    yield SQLAlchemyUserDatabase(session, User)
