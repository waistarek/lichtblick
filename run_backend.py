# -*- coding: utf-8 -*-
"""
Startskript für das FastAPI-Backend mit Uvicorn.

Erläuterung:
- Uvicorn ist ein ASGI-Server, der FastAPI-Anwendungen ausführt.
- Der Guard `if __name__ == "__main__":` stellt sicher, dass der Code nur ausgeführt
  wird, wenn diese Datei direkt gestartet wird (z. B. `python run_backend.py`),
  nicht beim Import als Modul.
- `uvicorn.run("backend.api:app", ...)` nutzt einen Import-String:
    * "backend.api"  = Python-Modulpfad zur Datei `backend/api.py`
    * "app"          = dort definierte FastAPI-Instanz (`app = FastAPI(...)`)
- `host="0.0.0.0"` bindet auf alle Netzwerkinterfaces (auch im LAN erreichbar).
- `port=8000` ist der TCP-Port (Zugriff z. B. via http://localhost:8000).
- `reload=True` aktiviert Auto-Reload bei Codeänderungen (nur für Entwicklung
  empfohlen; in Produktion deaktivieren oder einen Prozessmanager nutzen).
"""

import uvicorn  # ASGI-Server zum Starten der FastAPI-App

if __name__ == "__main__":
    # Startet den Server mit der App "app" im Modul "backend.api"
    uvicorn.run(
        "backend.api:app",  # Import-String: <modulpfad>:<app-variable>
        host="0.0.0.0",     # auf allen Interfaces lauschen
        port=8000,          # HTTP-Port
        reload=True         # automatisches Neustarten bei Codeänderungen (Dev)
    )
