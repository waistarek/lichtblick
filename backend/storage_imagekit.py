"""
Beschreibung:
- Initialisiert einen ImageKit-Client für Datei-Uploads und URL-Erzeugung.

Für Anfänger:
- Die Zugangsdaten (API-Schlüssel und URL-Endpunkt) werden aus der Umgebungsdatei `.env`
  in den Prozess geladen und anschließend aus den Umgebungsvariablen gelesen.
- In dieser Variante wird die Logik NICHT verändert, nur ausführlich kommentiert.

Voraussetzungen:
- Eine `.env`-Datei im Projektverzeichnis mit z. B.:
    IMAGEKIT_PRIVATE_KEY=...
    IMAGEKIT_PUBLIC_KEY=...
    IMAGEKIT_URL=https://ik.imagekit.io/<dein_endpoint>
- Paket-Abhängigkeiten:
    python-dotenv  (lädt .env)
    imagekitio     (ImageKit SDK)
"""

# Lädt Umgebungsvariablen aus einer .env-Datei in den aktuellen Prozess.
# Beispiel: Wenn in .env "FOO=bar" steht, ist danach os.getenv("FOO") -> "bar".
from dotenv import load_dotenv

# ImageKit Python SDK. Stellt die Klasse `ImageKit` bereit, die für
# Authentifizierung, Upload und URL-Generierung verwendet wird.
from imagekitio import ImageKit

# Standardbibliothek: Zugriff auf Umgebungsvariablen wie os.getenv("NAME").
import os

# Liest die in .env definierten Variablen und setzt sie in den Prozess-Kontext.
# Falls die Variablen bereits im OS-Umfeld gesetzt sind, überschreibt `load_dotenv`
# diese standardmäßig nicht (abhängig von den Parametern). Hier wird die
# Standardverwendung ohne Parameter genutzt.
load_dotenv()

# Erzeugt eine Instanz des ImageKit-Clients.
# Die drei wichtigsten Parameter:
#   - private_key: Geheimer Schlüssel (serverseitig verwenden, niemals im Frontend)
#   - public_key: Öffentlicher Schlüssel (darf clientseitig vorkommen)
#   - url_endpoint: Basis-URL deines ImageKit-Projekts (z. B. https://ik.imagekit.io/<endpoint>)
#
# WICHTIGER HINWEIS (nur Kommentar, keine Logikänderung):
#   In dieser Fassung wird `url_endpoint` als reiner String "IMAGEKIT_URL" gesetzt
#   und NICHT aus der Umgebung gelesen. Das bedeutet, der Client erhält buchstäblich
#   den Text "IMAGEKIT_URL" statt einer echten URL. In der Praxis führt das
#   typischerweise zu fehlerhaften URLs.
#
#   Üblicherweise würde man hier verwenden:
#       url_endpoint=os.getenv("IMAGEKIT_URL")
#   Da du explizit keine Logikänderung möchtest, bleibt es unverändert.
imagekit = ImageKit(
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY"),  # liest PRIVATE KEY aus .env
    public_key=os.getenv("IMAGEKIT_PUBLIC_KEY"),    # liest PUBLIC KEY aus .env
    url_endpoint=("IMAGEKIT_URL"),                  # HINWEIS: hier steht ein fester String, keine env-Auswertung
)

# Ab hier könntest du (in anderen Modulen) `imagekit` importieren und verwenden, z. B.:
#   from backend.storage_imagekit import imagekit
#   res = imagekit.upload_file(file=<bytes_or_stream>, file_name="bild.jpg")
#
# Typische Fehlerquellen:
# - Fehlende/verkehrte .env-Werte: os.getenv(...) gibt dann None zurück.
# - `url_endpoint` auf einem Literal-String statt echter URL (siehe Hinweis oben).
# - .env versehentlich committet (Sicherheitsrisiko). Immer in .gitignore eintragen.
