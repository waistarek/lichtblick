"""
Datei: backend/users.py (Beispielname)
Zweck:
- Zentrale Einrichtung der Benutzerverwaltung mit fastapi-users.
- Stellt Authentifizierung per JWT (JSON Web Token) bereit.
- Liefert Abhängigkeiten (Dependencies) wie `current_active_user` für geschützte Routen.

Für Anfänger:
- Lies die Kommentare Block für Block.
- Passe das SECRET über Umgebungsvariablen an (nicht hart codieren).
"""

import os
import uuid
import logging
from typing import Optional, AsyncGenerator

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, models
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase

# Diese beiden kommen aus deinem Projekt:
#   - `User`: dein User-ORM/Pydantic-Modell (SQLAlchemy-Userklasse, die fastapi-users erwartet)
#   - `get_user_db`: Dependency, die eine SQLAlchemyUserDatabase-Instanz liefert
from backend.database import User, get_user_db

# -----------------------------------------------------------------------------
# Konfiguration und Logging
# -----------------------------------------------------------------------------

# SECRET fürs Signieren der JWTs.
# Niemals einen echten Secret-Wert im Code fest verdrahten.
# Stattdessen aus der Umgebung lesen. Fallback nur für lokale Entwicklung.
JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-insecure-change-me")

# Token-Lebensdauer in Sekunden (z. B. 3600 = 1 Stunde)
JWT_LIFETIME_SECONDS: int = int(os.getenv("JWT_LIFETIME_SECONDS", "3600"))

# Logger statt print verwenden. Ausgabe steuerst du über Log-Level und Handler.
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# UserManager
# -----------------------------------------------------------------------------
# Der UserManager kapselt Benutzer-bezogene Hooks/Ereignisse (z. B. nach Registrierung).
# Er erbt:
#  - UUIDIDMixin: teilt fastapi-users mit, dass die User-IDs vom Typ UUID sind
#  - BaseUserManager[User, uuid.UUID]: generische Basisklasse für User-Management
# Du kannst hier z. B. E-Mails senden oder Auditing betreiben.
class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    # Secrets für Reset- und Verifizierungs-Tokens (separat vom JWT-Secret möglich)
    reset_password_token_secret = JWT_SECRET
    verification_token_secret = JWT_SECRET

    # Wird nach erfolgreicher Registrierung aufgerufen
    async def on_after_register(self, user: User, request: Optional[Request] = None) -> None:
        logger.info("User %s has registered.", user.id)

    # Wird nach Anforderung "Passwort vergessen" aufgerufen
    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ) -> None:
        # Achtung: Token nicht in reale Logs schreiben. Hier nur Demo.
        logger.info("User %s requested password reset. Reset token issued.", user.id)

    # Wird nach Anforderung einer Verifizierung aufgerufen
    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ) -> None:
        # Achtung: Token nicht in reale Logs schreiben. Hier nur Demo.
        logger.info("Verification requested for user %s.", user.id)


# Dependency-Fabrik: liefert pro Request einen UserManager
# Typannotationen helfen Einsteigern und Tools wie mypy.
async def get_user_manager(
    user_db: SQLAlchemyUserDatabase[models.UP, models.ID] = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    """
    Erzeugt einen UserManager, der intern `user_db` verwendet.
    Wird von fastapi-users intern für Auth- und User-Operationen genutzt.
    """
    yield UserManager(user_db)


# -----------------------------------------------------------------------------
# Authentifizierung: JWT über Bearer-Token
# -----------------------------------------------------------------------------

# 1) Transport: Bearer-Token im Authorization-Header
#    `tokenUrl` ist der Login-Endpunkt (wird in der OpenAPI angezeigt).
#    Je nach Router-Mount kann auch "/auth/jwt/login" nötig sein.
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

# 2) Strategie: JWT-Strategie mit Secret und Gültigkeitsdauer
def get_jwt_strategy() -> JWTStrategy:
    """
    Liefert die JWT-Strategie, die Tokens signiert und validiert.
    - secret: Schlüssel zum Signieren
    - lifetime_seconds: wie lange ein Token gültig ist
    """
    return JWTStrategy(secret=JWT_SECRET, lifetime_seconds=JWT_LIFETIME_SECONDS)

# 3) Backend: kombiniert Transport und Strategie
auth_backend = AuthenticationBackend(
    name="jwt",                      # beliebiger Name, z. B. "jwt"
    transport=bearer_transport,      # wie das Token übermittelt wird
    get_strategy=get_jwt_strategy,   # wie Tokens erzeugt/geprüft werden
)

# -----------------------------------------------------------------------------
# FastAPIUsers-Objekt und Dependencies für Routen
# -----------------------------------------------------------------------------

# Zentrales fastapi-users Objekt. Liefert u. a. Router und Abhängigkeiten.
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,   # Dependency-Fabrik für den UserManager
    [auth_backend],     # Liste der unterstützten Auth-Backends (hier nur JWT)
)

# Dependency für "geschützte Routen":
# - `active=True` erzwingt, dass der Benutzer aktiv ist.
# Weitere Varianten:
#   - `current_user()`         -> beliebiger eingeloggter User
#   - `current_superuser()`    -> erfordert Superuser-Rechte
current_active_user = fastapi_users.current_user(active=True)
