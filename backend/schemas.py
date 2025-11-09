"""
Beschreibung:
- Definiert Datenmodelle (Schemas) für Requests und Responses.
- Verwendet Pydantic BaseModel für Validierung und Serialisierung.
- Bindet fastapi-users Schemas für Benutzer-Objekte ein.

Für Anfänger:
- Ein "Schema" beschreibt die Form von Daten, die eine API (Application Programming Interface – Schnittstelle zwischen Softwarekomponenten)
  erwartet oder zurückgibt.
- Pydantic prüft automatisch Typen (z. B. str, int) und wandelt Eingaben, wo möglich, passend um.
- Die fastapi-users Schemas liefern fertige Felder und Validierungen für Benutzer (z. B. id, email).
"""

# Pydantic stellt BaseModel bereit: Damit definierst du klare, typgeprüfte Datenobjekte.
from pydantic import BaseModel

# fastapi-users bringt vorgefertigte Schemas für User mit (lesen, erstellen, aktualisieren).
from fastapi_users import schemas

# UUID (Universally Unique Identifier – universell eindeutiger Bezeichner)
# wird von fastapi-users für Benutzer-IDs verwendet.
import uuid


class PostCreate(BaseModel):
    """
    Schema für das Anlegen eines Posts.
    Dieses Modell wird typischerweise als Request-Body bei "POST /post" verwendet.
    """
    # Titel des Posts. Pflichtfeld (str).
    title: str

    # Inhalt/Text des Posts. Pflichtfeld (str).
    content: str


class PostResponse(BaseModel):
    """
    Schema für die Antwort eines Endpunkts, der einen Post zurückliefert.
    In einfachen Fällen spiegelt es PostCreate wider.
    Hinweis:
    - Hier sind nur title und content enthalten.
    - Optional könntest du in der Zukunft Felder wie id, created_at ergänzen.
      (Hier NICHT getan, da die Logik unverändert bleiben soll.)
    """
    # Titel des Posts.
    title: str

    # Inhalt/Text des Posts.
    content: str


class UserRead(schemas.BaseUser[uuid.UUID]):
    """
    Schema zum Auslesen eines Benutzers.
    Erbt von fastapi-users:
      - id: uuid.UUID
      - email: str
      - is_active: bool
      - is_superuser: bool
      - is_verified: bool
    Hinweis:
    - Wir fügen hier nichts hinzu (Logik unverändert).
    - Falls du später z. B. ein "username"-Feld brauchst, könntest du es ergänzen.
    """
    pass


class UserCreate(schemas.BaseUserCreate):
    """
    Schema zum Erstellen eines Benutzers.
    Erbt von fastapi-users:
      - email: str
      - password: str
    Optional können weitere Felder ergänzt werden (z. B. Benutzerprofilangaben),
    aber hier bleibt es unverändert.
    """
    pass


class UserUpdate(schemas.BaseUserUpdate):
    """
    Schema zum Aktualisieren eines Benutzers.
    Erbt von fastapi-users optionale Felder wie:
      - email: Optional[str]
      - password: Optional[str]
      - is_active / is_superuser / is_verified (je nach Konfiguration)
    Hier unverändert gelassen, damit die vorhandene Logik gleich bleibt.
    """
    pass
