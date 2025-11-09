# """
# Datei: frontend.py
# Zweck:
# - Streamlit-Frontend für eine kleine Social-App.
# - Login, Registrierung, Upload und Feed-Anzeige über HTTP-Requests gegen das FastAPI-Backend.

# Wichtig:
# - Die Logik bleibt unverändert. Nur Kommentare wurden ergänzt.
# - Diese Datei spricht hart kodiert mit http://localhost:8000. Für andere Umgebungen anpassen.
# - Das JWT (JSON Web Token) wird im Session-State abgelegt und bei Requests im Authorization-Header gesendet.
# """

# import streamlit as st
# import requests
# import base64
# import urllib.parse

# # Grundkonfiguration der Streamlit-Seite.
# # page_title: Tab-Titel im Browser
# # layout="wide": nutzt mehr horizontale Fläche
# st.set_page_config(page_title="Simple Social", layout="wide")

# # -----------------------------------------------------------------------------
# # Session State initialisieren
# # -----------------------------------------------------------------------------
# # Der Session State überlebt zwischen Interaktionen, solange die Session aktiv ist.
# # Wir speichern dort den JWT-Token und die User-Info nach erfolgreichem Login.
# if 'token' not in st.session_state:
#     st.session_state.token = None
# if 'user' not in st.session_state:
#     st.session_state.user = None


# def get_headers():
#     """
#     Liefert HTTP-Header für Requests gegen das Backend.
#     Wenn ein Token vorhanden ist, wird er als Bearer-Token gesetzt.
#     Rückgabe:
#         dict, z. B. {"Authorization": "Bearer <token>"} oder {} ohne Token.
#     """
#     if st.session_state.token:
#         return {"Authorization": f"Bearer {st.session_state.token}"}
#     return {}


# def login_page():
#     """
#     Zeigt die Login-/Registrierungsseite.
#     - Login sendet POST auf /auth/jwt/login mit Form-Daten username/password.
#     - Nach erfolgreichem Login wird /users/me aufgerufen, um Profildaten zu holen.
#     - Registrierung sendet POST auf /auth/register.
#     Hinweis:
#       Abhängig von der fastapi-users Konfiguration kann /auth/jwt/login statt 200 auch 204 liefern
#       und das Token nur als Cookie setzen. Diese UI erwartet eine JSON-Antwort mit access_token.
#       Logik wird hier nicht geändert, nur kommentiert.
#     """
#     st.title("🚀 Welcome to Simple Social")

#     # Einfache Eingabefelder für E-Mail und Passwort
#     email = st.text_input("Email:")
#     password = st.text_input("Password:", type="password")

#     # Buttons werden erst sinnvoll, wenn beide Felder befüllt sind
#     if email and password:
#         col1, col2 = st.columns(2)

#         with col1:
#             if st.button("Login", type="primary", use_container_width=True):
#                 # Login über den JWT-Endpunkt von fastapi-users
#                 # Achtung: Hier wird "username" verwendet, nicht "email". Das ist mit fastapi-users kompatibel.
#                 login_data = {"username": email, "password": password}
#                 response = requests.post("http://localhost:8000/auth/jwt/login", data=login_data)

#                 if response.status_code == 200:
#                     # Erwartet, dass die Antwort JSON mit "access_token" enthält.
#                     # Je nach fastapi-users Setup kann das abweichen.
#                     token_data = response.json()
#                     st.session_state.token = token_data["access_token"]

#                     # Nach dem Login die User-Infos laden
#                     user_response = requests.get("http://localhost:8000/users/me", headers=get_headers())
#                     if user_response.status_code == 200:
#                         st.session_state.user = user_response.json()
#                         # Neu rendern, damit die App in den "eingeloggt"-Zustand wechselt
#                         st.rerun()
#                     else:
#                         st.error("Failed to get user info")
#                 else:
#                     st.error("Invalid email or password!")

#         with col2:
#             if st.button("Sign Up", type="secondary", use_container_width=True):
#                 # Registrierung über fastapi-users
#                 signup_data = {"email": email, "password": password}
#                 response = requests.post("http://localhost:8000/auth/register", json=signup_data)

#                 if response.status_code == 201:
#                     st.success("Account created! Click Login now.")
#                 else:
#                     # Versuche, eine detaillierte Fehlermeldung zu zeigen
#                     try:
#                         error_detail = response.json().get("detail", "Registration failed")
#                     except Exception:
#                         error_detail = "Registration failed"
#                     st.error(f"Registration failed: {error_detail}")
#     else:
#         st.info("Enter your email and password above")


# def upload_page():
#     """
#     Zeigt die Upload-Seite.
#     - Akzeptiert Bilder und Videos.
#     - Sendet POST /upload mit Multipart-Daten: file und caption.
#     - Erwartet Status 200 bei Erfolg.
#     """
#     st.title("📸 Share Something")

#     # Datei-Upload-Komponente in Streamlit
#     uploaded_file = st.file_uploader(
#         "Choose media",
#         type=['png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov', 'mkv', 'webm']
#     )
#     # Freitext für die Bild- oder Videobeschreibung
#     caption = st.text_area("Caption:", placeholder="What's on your mind?")

#     if uploaded_file and st.button("Share", type="primary"):
#         with st.spinner("Uploading..."):
#             # Multipart-Form vorbereiten: files und data
#             files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
#             data = {"caption": caption}
#             response = requests.post(
#                 "http://localhost:8000/upload",
#                 files=files,
#                 data=data,
#                 headers=get_headers()
#             )

#             if response.status_code == 200:
#                 st.success("Posted!")
#                 # Aktualisiert die Seite, damit der neue Post im Feed erscheint
#                 st.rerun()
#             else:
#                 st.error("Upload failed!")


# def encode_text_for_overlay(text):
#     """
#     Kodiert Text für die Verwendung in ImageKit-Overlays.
#     Ablauf:
#       1) UTF-8 in Bytes
#       2) Base64-kodieren
#       3) URL-encoden
#     Rückgabe:
#       URL-sicherer base64-String oder "" wenn kein Text.
#     """
#     if not text:
#         return ""
#     # Schritt 1+2: Base64 aus dem UTF-8-String erzeugen
#     base64_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')
#     # Schritt 3: URL-sicher machen
#     return urllib.parse.quote(base64_text)


# def create_transformed_url(original_url, transformation_params, caption=None):
#     """
#     Erzeugt eine ImageKit-URL mit Transformationen.
#     - original_url: die vom Backend gespeicherte URL.
#     - transformation_params: Transformationsstring für ImageKit 'tr:'-Segment.
#     - caption: optionaler Text, der als Overlay eingeblendet werden kann.

#     Hinweis:
#       Wenn caption gesetzt ist, überschreibt diese Implementierung die transformation_params
#       mit einem Text-Overlay. Das ist so im Originalcode. Logik wird nicht geändert.
#     """
#     if caption:
#         encoded_caption = encode_text_for_overlay(caption)
#         # Text-Overlay am unteren Rand, halbtransparenter Hintergrund
#         text_overlay = f"l-text,ie-{encoded_caption},ly-N20,lx-20,fs-100,co-white,bg-000000A0,l-end"
#         transformation_params = text_overlay  # überschreibt ggf. vorhandene Parameter

#     # Falls keine Transformationen angegeben sind, gib die Original-URL zurück
#     if not transformation_params:
#         return original_url

#     # Vereinfachte Zerlegung der URL in Basis und Dateipfad
#     parts = original_url.split("/")

#     # parts[3] wird als imagekit_id genutzt, parts[4:] als Pfad
#     # Das setzt ein bestimmtes URL-Format voraus. In der Praxis prüfen.
#     imagekit_id = parts[3]  # ungenutzt, nur der Originalcode hat es so
#     file_path = "/".join(parts[4:])
#     base_url = "/".join(parts[:4])

#     # Transformationen werden als Segment "tr:<params>/" eingefügt
#     return f"{base_url}/tr:{transformation_params}/{file_path}"


# def feed_page():
#     """
#     Zeigt den Feed.
#     - Holt Daten per GET /feed.
#     - Zeigt pro Post Benutzer, Datum, Medien und optional einen Löschen-Button.
#     Hinweis:
#       Der Lösch-Request nutzt hier /posts/{id}. Das Backend definiert DELETE /post/{post_id} (Singular).
#       Das ist eine Inkonsistenz im Originalcode. Logik wird nicht geändert.
#     """
#     st.title("🏠 Feed")

#     response = requests.get("http://localhost:8000/feed", headers=get_headers())
#     if response.status_code == 200:
#         posts = response.json()["posts"]

#         if not posts:
#             st.info("No posts yet! Be the first to share something.")
#             return

#         for post in posts:
#             st.markdown("---")

#             # Kopfzeile: E-Mail des Erstellers, Datum, optional Löschen-Button
#             col1, col2 = st.columns([4, 1])
#             with col1:
#                 # created_at wird als ISO-String erwartet. [:10] zeigt YYYY-MM-DD.
#                 st.markdown(f"**{post['email']}** • {post['created_at'][:10]}")
#             with col2:
#                 if post.get('is_owner', False):
#                     if st.button("🗑️", key=f"delete_{post['id']}", help="Delete post"):
#                         # ACHTUNG: Hier wird /posts/{id} genutzt
#                         # Backend erwartet laut Beispiel /post/{post_id}.
#                         response = requests.delete(
#                             f"http://localhost:8000/posts/{post['id']}",
#                             headers=get_headers()
#                         )
#                         if response.status_code == 200:
#                             st.success("Post deleted!")
#                             st.rerun()
#                         else:
#                             st.error("Failed to delete post!")

#             # Medienanzeige mit optionalem Caption-Overlay
#             caption = post.get('caption', '')
#             if post['file_type'] == 'image':
#                 # Für Bilder direkte Anzeige mit optionalem Overlay
#                 uniform_url = create_transformed_url(post['url'], "", caption)
#                 st.image(uniform_url, width=300)
#             else:
#                 # Für Videos werden feste Transformationswerte gesetzt
#                 # Hier nur Beispielparameter. Logik bleibt wie im Original.
#                 uniform_video_url = create_transformed_url(
#                     post['url'],
#                     "w-400,h-200,cm-pad_resize,bg-blurred"
#                 )
#                 st.video(uniform_video_url, width=300)
#                 st.caption(caption)

#             st.markdown("")  # Abstand zwischen Posts
#     else:
#         st.error("Failed to load feed")


# # -----------------------------------------------------------------------------
# # Hauptlogik der App
# # -----------------------------------------------------------------------------
# # Wenn kein User im Session State, zeige die Login-Seite.
# # Sonst Sidebar mit Navigation und Logout.
# if st.session_state.user is None:
#     login_page()
# else:
#     # Sidebar mit Begrüßung und Navigation
#     st.sidebar.title(f"👋 Hi {st.session_state.user['email']}!")

#     # Logout setzt User und Token zurück und lädt die Seite neu
#     if st.sidebar.button("Logout"):
#         st.session_state.user = None
#         st.session_state.token = None
#         st.rerun()

#     st.sidebar.markdown("---")
#     page = st.sidebar.radio("Navigate:", ["🏠 Feed", "📸 Upload"])

#     if page == "🏠 Feed":
#         feed_page()
#     else:
#         upload_page()


########################################################################
###############################################################################
# """
# Streamlit-Frontend: Anmelden, Registrieren, Upload, Feed.
# Design vereinfacht, Texte auf Deutsch.
# Backend-URL per Umgebungsvariable BACKEND_URL konfigurierbar.
# """

# import os
# import base64
# import urllib.parse
# from datetime import datetime

# import requests
# import streamlit as st

# # ----------------------------
# # Grundeinstellungen
# # ----------------------------
# st.set_page_config(page_title="Simple Social", page_icon="🗨️", layout="wide")

# BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")

# if "token" not in st.session_state:
#     st.session_state.token = None
# if "user" not in st.session_state:
#     st.session_state.user = None


# # ----------------------------
# # Hilfsfunktionen (API)
# # ----------------------------
# def headers():
#     return {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}


# def api_login(email: str, password: str):
#     # fastapi-users JWT Login erwartet username/password als Form-Daten
#     r = requests.post(
#         f"{BACKEND_URL}/auth/jwt/login",
#         data={"username": email, "password": password},
#         timeout=15,
#     )
#     if r.status_code == 200:
#         return r.json().get("access_token")
#     return None


# def api_me():
#     r = requests.get(f"{BACKEND_URL}/users/me", headers=headers(), timeout=15)
#     return r.json() if r.ok else None


# def api_register(email: str, password: str):
#     r = requests.post(
#         f"{BACKEND_URL}/auth/register",
#         json={"email": email, "password": password},
#         timeout=15,
#     )
#     return r.status_code == 201, (r.json().get("detail") if r.headers.get("content-type","").startswith("application/json") else None)


# def api_feed():
#     r = requests.get(f"{BACKEND_URL}/feed", headers=headers(), timeout=20)
#     return r.json().get("posts", []) if r.ok else []


# def api_upload(file, caption: str):
#     files = {"file": (file.name, file.getvalue(), file.type)}
#     data = {"caption": caption}
#     r = requests.post(f"{BACKEND_URL}/upload", files=files, data=data, headers=headers(), timeout=60)
#     return r.ok


# def api_delete(post_id: str):
#     # Backend definiert DELETE /post/{post_id}
#     r = requests.delete(f"{BACKEND_URL}/post/{post_id}", headers=headers(), timeout=20)
#     return r.ok


# # ----------------------------
# # UI-Hilfen
# # ----------------------------
# def encode_text_for_overlay(text: str) -> str:
#     if not text:
#         return ""
#     return urllib.parse.quote(base64.b64encode(text.encode("utf-8")).decode("utf-8"))


# def imgkit_url(original_url: str, transformation_params: str, caption: str | None = None) -> str:
#     # Optionales Text-Overlay (wie im bisherigen Code)
#     if caption:
#         encoded = encode_text_for_overlay(caption)
#         transformation_params = f"l-text,ie-{encoded},ly-N20,lx-20,fs-100,co-white,bg-000000A0,l-end"

#     if not transformation_params:
#         return original_url

#     parts = original_url.split("/")
#     if len(parts) < 5:
#         return original_url
#     base_url = "/".join(parts[:4])
#     file_path = "/".join(parts[4:])
#     return f"{base_url}/tr:{transformation_params}/{file_path}"


# def is_image_post(post: dict) -> bool:
#     # Backend liefert teils falsches Feld file_type. Fallback über Dateiendung.
#     t = (post.get("file_type") or "").lower()
#     if t == "image":
#         return True
#     url = (post.get("url") or "").lower().split("?")[0]
#     return url.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))


# # ----------------------------
# # Seiten
# # ----------------------------
# def page_auth():
#     st.title("Anmeldung")

#     tab_login, tab_signup = st.tabs(["Anmelden", "Registrieren"])

#     with tab_login:
#         col1, col2 = st.columns([1, 1])
#         with col1:
#             email = st.text_input("E-Mail")
#             pw = st.text_input("Passwort", type="password")
#             if st.button("Anmelden", type="primary", use_container_width=True, disabled=not (email and pw)):
#                 token = api_login(email, pw)
#                 if token:
#                     st.session_state.token = token
#                     user = api_me()
#                     if user:
#                         st.session_state.user = user
#                         st.rerun()
#                     else:
#                         st.error("Profil konnte nicht geladen werden.")
#                 else:
#                     st.error("E-Mail oder Passwort ist falsch.")
#         with col2:
#             st.info("Nutze die Registrierung, wenn du noch keinen Zugang hast.")

#     with tab_signup:
#         col1, col2 = st.columns([1, 1])
#         with col1:
#             email_r = st.text_input("E-Mail (neu)")
#             pw_r = st.text_input("Passwort (neu)", type="password")
#             if st.button("Konto erstellen", use_container_width=True, disabled=not (email_r and pw_r)):
#                 ok, detail = api_register(email_r, pw_r)
#                 if ok:
#                     st.success("Konto erstellt. Bitte oben anmelden.")
#                 else:
#                     st.error(f"Registrierung fehlgeschlagen: {detail or 'Unbekannter Fehler'}")
#         with col2:
#             st.caption("Passwort sicher wählen. Zugangsdaten nicht teilen.")


# def page_upload():
#     st.title("Beitrag erstellen")
#     st.caption("Teile ein Bild oder Video mit optionaler Beschreibung.")

#     col_left, col_right = st.columns([2, 1])

#     with col_left:
#         file = st.file_uploader(
#             "Datei auswählen",
#             type=["png", "jpg", "jpeg", "gif", "webp", "mp4", "avi", "mov", "mkv", "webm"],
#         )
#         caption = st.text_area("Beschreibung", placeholder="Was möchtest du teilen?")
#         send = st.button("Teilen", type="primary", disabled=not file)

#     with col_right:
#         st.info("Hinweis\n\n• Erlaubte Formate siehe oben\n• Große Videos benötigen länger")

#     if file and send:
#         with st.spinner("Upload läuft…"):
#             ok = api_upload(file, caption)
#         if ok:
#             st.success("Beitrag veröffentlicht.")
#             st.rerun()
#         else:
#             st.error("Upload fehlgeschlagen.")


# def page_feed():
#     st.title("Feed")
#     posts = api_feed()
#     if not posts:
#         st.info("Noch keine Beiträge vorhanden.")
#         return

#     for post in posts:
#         with st.container(border=True):
#             top = st.columns([6, 2])
#             with top[0]:
#                 email = post.get("email", "Unbekannt")
#                 dt = post.get("created_at", "")
#                 try:
#                     dt_disp = datetime.fromisoformat(dt.replace("Z", "+00:00")).strftime("%d.%m.%Y %H:%M")
#                 except Exception:
#                     dt_disp = dt[:16]
#                 st.markdown(f"**{email}** · {dt_disp}")
#             with top[1]:
#                 if post.get("is_owner"):
#                     if st.button("Löschen", key=f"del_{post['id']}", use_container_width=True):
#                         if api_delete(post["id"]):
#                             st.success("Beitrag gelöscht.")
#                             st.rerun()
#                         else:
#                             st.error("Löschen fehlgeschlagen.")

#             caption = post.get("caption") or ""

#             if is_image_post(post):
#                 # Bild mit optionalem Overlay
#                 url = imgkit_url(post["url"], "", caption=None)  # Overlay weggelassen für klare Anzeige
#                 st.image(url, use_container_width=True)
#                 if caption:
#                     st.caption(caption)
#             else:
#                 # Video
#                 vurl = imgkit_url(post["url"], "w-800,h-450,cm-pad_resize,bg-blurred")
#                 st.video(vurl)
#                 if caption:
#                     st.caption(caption)


# # ----------------------------
# # App-Flow
# # ----------------------------
# with st.sidebar:
#     st.subheader("Simple Social")
#     st.caption(f"Backend: {BACKEND_URL}")

#     if st.session_state.user:
#         st.markdown(f"Angemeldet als **{st.session_state.user.get('email','?')}**")
#         if st.button("Abmelden", use_container_width=True):
#             st.session_state.user = None
#             st.session_state.token = None
#             st.rerun()
#         st.divider()
#         route = st.radio("Navigation", ["Feed", "Beitrag erstellen"], label_visibility="visible")
#     else:
#         route = "auth"

# if st.session_state.user is None or route == "auth":
#     page_auth()
# else:
#     if route == "Feed":
#         page_feed()
#     elif route == "Beitrag erstellen":
#         page_upload()
################################################################################
########################################################################

# Likes + Dislikes + Kommentare (sichtbar), Dark-Mode Toggle, „Beiträge“.
# Fix: Kommentar-Posten als Form ohne disabled-Button, kein SessionState-Reset nach Widget-Init.
# ------------------------------------------------------------------------------
# Diese Streamlit-App ist ein kleines Social-Frontend namens „Lichtblick“.
# Sie spricht mit einem FastAPI-Backend und bietet:
# - Anmeldung/Registrierung (FastAPI Users, JWT)
# - Beiträge anzeigen („Beiträge“ statt „Feed“)
# - Upload von Bild/Video + Beschreibung
# - Likes UND Dislikes (wechselseitig exklusiv)
# - Kommentare lesen und schreiben
# - Hell-/Dunkelmodus per CSS-Variablen
#
# Wichtig:
# - Alle Aufrufe zu optionalen Endpunkten (/like, /unlike, /dislike, /undislike, /comments)
#   haben Fallbacks auf „lokalen Zustand“, falls dein Backend diese Endpunkte noch nicht hat.
#   So bleibt die UI benutzbar, auch wenn das Backend diese Features (noch) nicht anbietet.
# - Kommentare werden über ein Formular mit clear_on_submit gepostet, um den
#   Streamlit-SessionState-Fehler zu vermeiden („cannot be modified after widget...“).
# ------------------------------------------------------------------------------

import os
import base64
import urllib.parse
from datetime import datetime
from typing import Optional, Dict, List

import requests
import streamlit as st

# ------------------------------------------------------------
# Grundeinstellungen
# ------------------------------------------------------------
APP_NAME = "Lichtblick"  # Anzeigename der App
# Backend-Basis-URL. Standard ist lokales FastAPI unter Port 8000.
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
# Grundlayout der Streamlit-Seite
st.set_page_config(page_title=APP_NAME, page_icon="🌤️", layout="wide")

# Session-Defaults
# Hinweis: st.session_state ist der persistente Zustand zwischen UI-Runs.
# Wir legen Standardwerte nur einmal an (setdefault).
st.session_state.setdefault("token", None)               # JWT aus /auth/jwt/login
st.session_state.setdefault("user", None)                # JSON von /users/me
st.session_state.setdefault("theme", "light")            # "light" oder "dark"
st.session_state.setdefault("beitraege", [])             # gecachter Beitrags-Feed
# Informationen, ob das Backend Like/Dislike/Comments unterstützt. None=unbekannt.
st.session_state.setdefault("api_support", {"like": None, "dislike": None, "comments": None})
# Lokaler Zustand für Reaktionen je Post, falls Backend-Endpunkte fehlen.
# Struktur: {post_id: {"is_liked": bool, "likes": int, "is_disliked": bool, "dislikes": int}}
st.session_state.setdefault("local_reacts", {})
# Lokaler Kommentar-Speicher als Fallback, falls Backend-Kommentare fehlen.
st.session_state.setdefault("local_comments", {})        # {post_id: [{"author":..., "text":...}]}
# Cache für Server-Kommentare, um unnötige GETs zu vermeiden.
st.session_state.setdefault("comments_cache", {})        # {post_id: [...]}

def _rerun():
    """Sicherer Neu-Render der App. Streamlit-Versionen variieren in API-Namen."""
    try:
        st.rerun()
    except Exception:
        try:
            st.experimental_rerun()
        except Exception:
            pass

# ------------------------------------------------------------
# Styling (Light/Dark via CSS-Variablen)
# ------------------------------------------------------------
# Die beiden CSS-Blöcke definieren die Farbvariablen und Basiskomponenten
# für Hell- und Dunkelmodus. Der eigentliche Wechsel geschieht später,
# indem wir je nach st.session_state["theme"] den entsprechenden Block einbinden.

LIGHT_CSS = """
<style>
:root{
  --radius:14px;
  --bg:#f6f8fc;
  --card:#ffffff;
  --line:#e6e9f0;
  --text:#0f172a;
  --muted:#6b7280;
  --muted2:#68728a;
  --primary:#2563eb; /* Blau */
  --accent:#f97316;  /* Koralle */
}
.block-container{ max-width:1180px; padding-top:1.2rem; }
.ss-hero{
  border-radius:var(--radius); padding:22px 20px; margin-bottom:18px;
  background:linear-gradient(180deg,#eef2ff 0%, #ffffff 65%);
  border:1px solid var(--line); color:var(--text);
}
.ss-card{
  border-radius:var(--radius); padding:14px 16px 16px; margin-bottom:14px;
  background:var(--card); border:1px solid var(--line);
  box-shadow:0 6px 22px rgba(16,24,40,0.06); color:var(--text);
}
.ss-muted{ color:var(--muted); font-size:13px; }
.ss-badge{
  display:inline-block; padding:.26rem .6rem; border-radius:999px;
  border:1px solid var(--line); background:#f8fafc; font-size:12px; color:var(--primary);
}
.stButton>button{ border-radius:10px; border:1px solid var(--line); }
.stButton>button:hover{ border-color:var(--primary); color:var(--primary); }
.primary>button{
  background:var(--primary) !important; color:#fff !important; border:1px solid var(--primary) !important;
}
.danger>button{
  background:#fff5f5 !important; color:#b91c1c !important; border:1px solid #fecaca !important;
}
.ss-media img, .ss-media video{ border-radius:12px; }
.sep{ margin:10px 0; border-top:1px solid var(--line); }
</style>
"""

DARK_CSS = """
<style>
:root{
  --radius:14px;
  --bg:#0b1220;
  --card:#0f1729;
  --line:#1f2a3a;
  --text:#e5edf7;
  --muted:#9aa3b2;
  --muted2:#a8b3c3;
  --primary:#60a5fa; /* helleres Blau */
  --accent:#fb923c;  /* hellere Koralle */
}
.block-container{ max-width:1180px; padding-top:1.2rem; }
.ss-hero{
  border-radius:var(--radius); padding:22px 20px; margin-bottom:18px;
  background:linear-gradient(180deg,#0b1530 0%, #0f1729 65%);
  border:1px solid var(--line); color:var(--text);
}
.ss-card{
  border-radius:var(--radius); padding:14px 16px 16px; margin-bottom:14px;
  background:var(--card); border:1px solid var(--line);
  box-shadow:0 10px 24px rgba(0,0,0,0.35); color:var(--text);
}
.ss-muted{ color:var(--muted); font-size:13px; }
.ss-badge{
  display:inline-block; padding:.26rem .6rem; border-radius:999px;
  border:1px solid var(--line); background:#101a2f; font-size:12px; color:var(--primary);
}
.stButton>button{ border-radius:10px; border:1px solid var(--line); background:#121a2e; color:var(--text); }
.stButton>button:hover{ border-color:var(--primary); color:var(--primary); }
.primary>button{
  background:var(--primary) !important; color:#0b1220 !important; border:1px solid var(--primary) !important;
}
.danger>button{
  background:#2a1214 !important; color:#fecaca !important; border:1px solid #7f1d1d !important;
}
.ss-media img, .ss-media video{ border-radius:12px; }
.sep{ margin:10px 0; border-top:1px solid var(--line); }
</style>
"""

# Einbinden des passenden Styles entsprechend dem aktiven Theme.
st.markdown(DARK_CSS if st.session_state["theme"] == "dark" else LIGHT_CSS, unsafe_allow_html=True)

# ------------------------------------------------------------
# API-Helfer
# ------------------------------------------------------------
def _headers() -> Dict[str, str]:
    """Erzeuge Standard-HTTP-Header inklusive Authorization, falls Token vorhanden."""
    t = st.session_state["token"]
    return {"Authorization": f"Bearer {t}"} if t else {}

def _safe_request(method: str, url: str, **kwargs) -> Optional[requests.Response]:
    """
    Wrapper um requests.request mit Timeout und Fehlerbehandlung.
    Liefert None bei Netzwerkfehlern, damit die UI sauber bleibt.
    """
    timeout = kwargs.pop("timeout", 20)
    try:
        return requests.request(method, url, timeout=timeout, **kwargs)
    except requests.exceptions.RequestException as exc:
        st.error(f"Netzwerkfehler: {exc}")
        return None

def api_login(email: str, password: str) -> Optional[str]:
    """Login am Backend. Gibt JWT-Access-Token zurück oder None bei Fehler."""
    r = _safe_request("post", f"{BACKEND_URL}/auth/jwt/login",
                      data={"username": email, "password": password}, timeout=15)
    if r and r.status_code == 200:
        return r.json().get("access_token")
    return None

def api_me() -> Optional[Dict]:
    """Hole Benutzerprofil des eingeloggten Users."""
    r = _safe_request("get", f"{BACKEND_URL}/users/me", headers=_headers(), timeout=15)
    return r.json() if r and r.ok else None

def api_register(email: str, password: str) -> (bool, Optional[str]):
    """Registriere neuen User. Liefert (True,None) bei Erfolg oder (False,Detail) bei Fehler."""
    r = _safe_request("post", f"{BACKEND_URL}/auth/register",
                      json={"email": email, "password": password}, timeout=15)
    if r and r.status_code == 201:
        return True, None
    if r:
        try:
            return False, r.json().get("detail")
        except Exception:
            return False, f"Status {r.status_code}"
    return False, "Netzwerkfehler"

def api_beitraege() -> List[Dict]:
    """
    Hole Beiträge vom Backend (/feed).
    Ergänze Standardfelder, falls Backend sie nicht liefert.
    """
    r = _safe_request("get", f"{BACKEND_URL}/feed", headers=_headers(), timeout=25)
    if r and r.ok:
        data = r.json()
        posts = data.get("posts", [])
        for p in posts:
            p["id"] = str(p.get("id"))
            p.setdefault("likes", 0)
            p.setdefault("is_liked", False)
            p.setdefault("dislikes", 0)
            p.setdefault("is_disliked", False)
        return posts
    return []

def api_upload(file, caption: str) -> bool:
    """Lade Datei + Beschriftung hoch (/upload)."""
    files = {"file": (file.name, file.getvalue(), file.type)}
    data = {"caption": caption}
    r = _safe_request("post", f"{BACKEND_URL}/upload", files=files, data=data, headers=_headers(), timeout=120)
    return bool(r and r.ok)

def api_delete(post_id: str) -> bool:
    """Lösche Beitrag (/post/{id})."""
    r = _safe_request("delete", f"{BACKEND_URL}/post/{post_id}", headers=_headers(), timeout=20)
    return bool(r and r.ok)

# Likes / Dislikes optional (Fallback lokal)
# Die folgenden Funktionen versuchen zuerst den Backend-Endpunkt.
# Wenn /post/{id}/like (oder /unlike, /dislike, /undislike) 404 liefert,
# markieren wir die Funktionalität als „nicht unterstützt“ und nutzen nur Lokalzustand.

def api_like(post_id: str) -> Optional[bool]:
    r = _safe_request("post", f"{BACKEND_URL}/post/{post_id}/like", headers=_headers(), timeout=12)
    if not r: return None
    if r.status_code == 404:
        st.session_state["api_support"]["like"] = False
        return None
    st.session_state["api_support"]["like"] = True
    return bool(r.ok)

def api_unlike(post_id: str) -> Optional[bool]:
    r = _safe_request("post", f"{BACKEND_URL}/post/{post_id}/unlike", headers=_headers(), timeout=12)
    if not r: return None
    if r.status_code == 404:
        st.session_state["api_support"]["like"] = False
        return None
    st.session_state["api_support"]["like"] = True
    return bool(r.ok)

def api_dislike(post_id: str) -> Optional[bool]:
    r = _safe_request("post", f"{BACKEND_URL}/post/{post_id}/dislike", headers=_headers(), timeout=12)
    if not r: return None
    if r.status_code == 404:
        st.session_state["api_support"]["dislike"] = False
        return None
    st.session_state["api_support"]["dislike"] = True
    return bool(r.ok)

def api_undislike(post_id: str) -> Optional[bool]:
    r = _safe_request("post", f"{BACKEND_URL}/post/{post_id}/undislike", headers=_headers(), timeout=12)
    if not r: return None
    if r.status_code == 404:
        st.session_state["api_support"]["dislike"] = False
        return None
    st.session_state["api_support"]["dislike"] = True
    return bool(r.ok)

def api_comments(post_id: str) -> Optional[List[Dict]]:
    """
    Hole Kommentare zu einem Beitrag. Liefert None bei Fehler oder wenn
    Backend-Kommentare nicht unterstützt werden (404).
    """
    r = _safe_request("get", f"{BACKEND_URL}/post/{post_id}/comments", headers=_headers(), timeout=12)
    if not r: return None
    if r.status_code == 404:
        st.session_state["api_support"]["comments"] = False
        return None
    st.session_state["api_support"]["comments"] = True
    if r.ok:
        return r.json().get("comments", [])
    return None

def api_add_comment(post_id: str, text: str) -> Optional[bool]:
    """
    Füge Kommentar hinzu. True bei Erfolg, False bei Backend-Fehler,
    None bei Netzwerkfehler oder Nicht-Unterstützung (404 -> merken).
    """
    payload = {"text": text}
    r = _safe_request("post", f"{BACKEND_URL}/post/{post_id}/comments", headers=_headers(), json=payload, timeout=12)
    if not r: return None
    if r.status_code == 404:
        st.session_state["api_support"]["comments"] = False
        return None
    st.session_state["api_support"]["comments"] = True
    return bool(r.ok)

# ------------------------------------------------------------
# UI-Helfer
# ------------------------------------------------------------
def avatar_url(email: str) -> str:
    """Erzeuge eine Initialen-Avatar-URL über dicebear."""
    seed = urllib.parse.quote(email or "user")
    return f"https://api.dicebear.com/7.x/initials/svg?seed={seed}&radius=50"

def fmt_dt(iso: str) -> str:
    """ISO-String sauber formatiert (dd.mm.yyyy HH:MM). Fallback: roh zuschneiden."""
    if not iso: return ""
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%d.%m.%Y %H:%M")
    except Exception:
        return iso[:16]

def is_image_post(post: Dict) -> bool:
    """Grobe Erkennung, ob der Beitrag ein Bild ist."""
    t = (post.get("file_type") or "").lower()
    if t == "image":
        return True
    url = (post.get("url") or "").lower().split("?")[0]
    return url.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))

# Reaktionen lokal anwenden (inkl. Exklusivität Like vs Dislike)
# Diese Funktionen ändern NUR den lokalen UI-Zustand, damit sich die App „snappy“ anfühlt.
# Backend-Aufrufe werden zusätzlich versucht; bei deren Fehlschlag wird rückgängig gemacht.

def _ensure_local_state(post_id: str, likes: int, is_liked: bool, dislikes: int, is_disliked: bool):
    """Sorge dafür, dass für den Post eine lokale Reaktions-Struktur existiert."""
    st.session_state["local_reacts"].setdefault(post_id, {
        "likes": likes, "is_liked": is_liked, "dislikes": dislikes, "is_disliked": is_disliked
    })

def _apply_local(post_id: str, *, like: Optional[bool] = None, dislike: Optional[bool] = None):
    """
    Wende eine lokale Änderung für Like/Dislike an.
    Exklusivität: Aktivieren von Like deaktiviert Dislike und umgekehrt.
    """
    for p in st.session_state["beitraege"]:
        if p.get("id") == post_id:
            _ensure_local_state(post_id, p.get("likes", 0), p.get("is_liked", False), p.get("dislikes", 0), p.get("is_disliked", False))
            state = st.session_state["local_reacts"][post_id]

            # Like-Änderung
            if like is not None:
                if like and not state["is_liked"]:
                    state["is_liked"] = True
                    state["likes"] += 1
                    # Dislike ggf. zurücknehmen
                    if state["is_disliked"]:
                        state["is_disliked"] = False
                        state["dislikes"] = max(0, state["dislikes"] - 1)
                elif not like and state["is_liked"]:
                    state["is_liked"] = False
                    state["likes"] = max(0, state["likes"] - 1)

            # Dislike-Änderung
            if dislike is not None:
                if dislike and not state["is_disliked"]:
                    state["is_disliked"] = True
                    state["dislikes"] += 1
                    # Like ggf. zurücknehmen
                    if state["is_liked"]:
                        state["is_liked"] = False
                        state["likes"] = max(0, state["likes"] - 1)
                elif not dislike and state["is_disliked"]:
                    state["is_disliked"] = False
                    state["dislikes"] = max(0, state["dislikes"] - 1)

            # Änderungen zurück in die Beitragsliste schreiben
            p["likes"] = state["likes"]
            p["is_liked"] = state["is_liked"]
            p["dislikes"] = state["dislikes"]
            p["is_disliked"] = state["is_disliked"]
            break

def toggle_like(post_id: str):
    """
    Like-Toggle mit optimistischer UI-Aktualisierung.
    Bei Backend-Fehler ggf. lokale Änderung wieder zurückdrehen.
    """
    p = next((x for x in st.session_state["beitraege"] if x.get("id") == post_id), None)
    if not p: return
    currently = bool(p.get("is_liked", False))
    if currently:
        _apply_local(post_id, like=False)
        remote = api_unlike(post_id)
        if remote is False:
            _apply_local(post_id, like=True)
    else:
        _apply_local(post_id, like=True)
        rl = api_like(post_id)
        # Wenn Dislike aktiv war und Backend Dislike unterstützt, versuche Undislike
        if rl is not False and st.session_state["api_support"]["dislike"] is not False and (p.get("is_disliked") or st.session_state["local_reacts"].get(post_id,{}).get("is_disliked")):
            api_undislike(post_id)
        if rl is False:
            _apply_local(post_id, like=False)

def toggle_dislike(post_id: str):
    """
    Dislike-Toggle mit optimistischer UI-Aktualisierung.
    Bei Backend-Fehler ggf. lokale Änderung wieder zurückdrehen.
    """
    p = next((x for x in st.session_state["beitraege"] if x.get("id") == post_id), None)
    if not p: return
    currently = bool(p.get("is_disliked", False))
    if currently:
        _apply_local(post_id, dislike=False)
        remote = api_undislike(post_id)
        if remote is False:
            _apply_local(post_id, dislike=True)
    else:
        _apply_local(post_id, dislike=True)
        rd = api_dislike(post_id)
        # Wenn Like aktiv war und Backend Likes unterstützt, versuche Unlike
        if rd is not False and st.session_state["api_support"]["like"] is not False and (p.get("is_liked") or st.session_state["local_reacts"].get(post_id,{}).get("is_liked")):
            api_unlike(post_id)
        if rd is False:
            _apply_local(post_id, dislike=False)

# Kommentare holen/zwischenspeichern
def get_comments(post_id: str) -> List[Dict]:
    """
    Hole Kommentare aus Server-Cache oder Backend.
    Fällt zurück auf lokale Kommentare, falls Backend nicht unterstützt/erreichbar.
    """
    if st.session_state["api_support"]["comments"] is not False:
        if post_id not in st.session_state["comments_cache"]:
            data = api_comments(post_id)
            if data is not None:
                st.session_state["comments_cache"][post_id] = data
        if post_id in st.session_state["comments_cache"]:
            return st.session_state["comments_cache"][post_id]
    return st.session_state["local_comments"].get(post_id, [])

def add_comment(post_id: str, text: str, author: str):
    """
    Kommentar hinzufügen: erst Backend versuchen, bei Misserfolg lokal speichern.
    Gibt True bei Erfolg, sonst False.
    """
    text = (text or "").strip()
    if not text:
        return False
    ok = None
    if st.session_state["api_support"]["comments"] is not False:
        ok = api_add_comment(post_id, text)
        if ok:
            # Server-Kommentare invalidieren, damit nach Posten frisch geladen wird
            st.session_state["comments_cache"].pop(post_id, None)
            return True
        if ok is False:
            return False
    # Fallback: lokal ablegen
    st.session_state["local_comments"].setdefault(post_id, []).append({"author": author, "text": text})
    return True

# ------------------------------------------------------------
# Komponenten
# ------------------------------------------------------------
def top_hero():
    """Oberer Kopfbereich mit Titel, Slogan, Backend-Tag und Theme-Umschalter."""
    st.markdown('<div class="ss-hero">', unsafe_allow_html=True)
    c1, c2 = st.columns([3.2, 1])
    with c1:
        st.markdown(f"## {APP_NAME}")
        st.markdown("**Teile Bilder und Videos – schnell, einfach, privat.**")
        st.markdown(f'<span class="ss-badge">Backend: {BACKEND_URL}</span>', unsafe_allow_html=True)
    with c2:
        label = "Dunkelmodus" if st.session_state["theme"] == "light" else "Hellmodus"
        if st.button(label, use_container_width=True):
            st.session_state["theme"] = "dark" if st.session_state["theme"] == "light" else "light"
            _rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def page_auth():
    """Seite für Anmeldung und Registrierung."""
    top_hero()
    tab_login, tab_signup = st.tabs(["Anmelden", "Registrieren"])

    with tab_login:
        st.info("Bitte melde dich an.")
        email = st.text_input("E-Mail")
        pw = st.text_input("Passwort", type="password")
        with st.container():
            st.markdown('<div class="primary">', unsafe_allow_html=True)
            if st.button("Anmelden", use_container_width=True):
                if not (email and pw):
                    st.warning("Bitte E-Mail und Passwort eingeben.")
                else:
                    token = api_login(email, pw)
                    if token:
                        st.session_state["token"] = token
                        user = api_me()
                        if user:
                            st.session_state["user"] = user
                            st.success("Erfolgreich angemeldet.")
                            _rerun()
                        else:
                            st.error("Profil konnte nicht geladen werden.")
                    else:
                        st.error("E-Mail oder Passwort ist falsch.")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_signup:
        st.info("Neues Konto erstellen.")
        email_r = st.text_input("E-Mail (neu)")
        pw_r = st.text_input("Passwort (neu)", type="password")
        if st.button("Konto erstellen", use_container_width=True):
            if not (email_r and pw_r):
                st.warning("Bitte E-Mail und Passwort eingeben.")
            else:
                ok, detail = api_register(email_r, pw_r)
                if ok:
                    st.success("Konto erstellt. Jetzt im Reiter „Anmelden“ einloggen.")
                else:
                    st.error(f"Registrierung fehlgeschlagen: {detail or 'Unbekannter Fehler'}")

def page_upload():
    """Seite zum Erstellen eines neuen Beitrags mit Datei-Upload und Beschreibung."""
    top_hero()
    st.subheader("Beitrag erstellen")
    st.caption("Bild oder Video hochladen und optional beschreiben.")

    left, right = st.columns([2, 1])
    with left:
        uploaded = st.file_uploader(
            "Datei auswählen",
            type=["png","jpg","jpeg","gif","webp","mp4","avi","mov","mkv","webm"]
        )
        caption = st.text_area("Beschreibung", placeholder="Was möchtest du teilen?")

        if uploaded:
            # Vorschau des gewählten Mediums
            st.markdown("**Vorschau**")
            if uploaded.type.startswith("image/"):
                st.image(uploaded, use_container_width=True)
            else:
                st.video(uploaded)
            size_mb = round(getattr(uploaded, "size", 0) / 1024 / 1024, 2)
            st.caption(f"Datei: {uploaded.name} • Typ: {uploaded.type} • Größe: ~{size_mb} MB")

        with st.container():
            st.markdown('<div class="primary">', unsafe_allow_html=True)
            if st.button("Teilen", use_container_width=True, disabled=not uploaded):
                # Upload anstoßen
                with st.spinner("Upload läuft…"):
                    ok = api_upload(uploaded, caption or "")
                if ok:
                    st.success("Beitrag veröffentlicht.")
                    # Beiträge neu laden, damit der neue Beitrag erscheint
                    st.session_state["beitraege"] = api_beitraege()
                    _rerun()
                else:
                    st.error("Upload fehlgeschlagen.")
            st.markdown('</div>', unsafe_allow_html=True)

    with right:
        # Seitliche Hinweise
        st.markdown('<div class="ss-card">', unsafe_allow_html=True)
        st.markdown("**Tipps**")
        st.markdown(
            "- Erlaubte Formate: Bilder & Videos\n"
            "- Große Dateien brauchen länger\n"
            "- Nur Inhalte hochladen, an denen du Rechte besitzt"
        )
        st.markdown("</div>", unsafe_allow_html=True)

def render_post_card(post: Dict):
    """Eine einzelne Beitragskarte mit Kopf, Medien, Reaktionen und Kommentaren."""
    st.markdown('<div class="ss-card">', unsafe_allow_html=True)

    # Kopfzeile mit Avatar, Autor + Zeit und ggf. Lösch-Button
    head = st.columns([0.9, 4, 1.4])
    with head[0]:
        st.image(avatar_url(post.get("email", "")), width=44)
    with head[1]:
        st.markdown(f"**{post.get('email','Unbekannt')}**")
        st.markdown(f'<span class="ss-muted">{fmt_dt(post.get("created_at",""))}</span>', unsafe_allow_html=True)
    with head[2]:
        if post.get("is_owner"):
            with st.container():
                st.markdown('<div class="danger">', unsafe_allow_html=True)
                if st.button("Löschen", key=f"del_{post['id']}", use_container_width=True):
                    if api_delete(post["id"]):
                        st.success("Beitrag gelöscht.")
                        # Entferne den Beitrag aus dem lokalen Cache
                        st.session_state["beitraege"] = [p for p in st.session_state["beitraege"] if p.get("id") != post["id"]]
                        _rerun()
                    else:
                        st.error("Löschen fehlgeschlagen.")
                st.markdown('</div>', unsafe_allow_html=True)

    # Medienbereich
    st.markdown('<div class="ss-media">', unsafe_allow_html=True)
    if is_image_post(post):
        st.image(post.get("url",""), use_container_width=True)
    else:
        st.video(post.get("url",""))
    st.markdown('</div>', unsafe_allow_html=True)

    # Beschreibung anzeigen
    if post.get("caption"):
        st.markdown(f"<div class='ss-muted' style='margin-top:8px;'>{post['caption']}</div>", unsafe_allow_html=True)

    # Reaktionen: Like, Dislike, Download
    likes = int(post.get("likes", 0) or 0)
    dislikes = int(post.get("dislikes", 0) or 0)
    is_liked = bool(post.get("is_liked", False))
    is_disliked = bool(post.get("is_disliked", False))

    r1, r2, r3 = st.columns([1,1,1])
    with r1:
        label = f"♥️ {likes}" if is_liked else f"♡ {likes}"
        if st.button(label, key=f"like_{post['id']}", use_container_width=True):
            toggle_like(post["id"])
            _rerun()
    with r2:
        label_d = f"👎 {dislikes}"
        if st.button(label_d, key=f"dislike_{post['id']}", use_container_width=True):
            toggle_dislike(post["id"])
            _rerun()
    with r3:
        if st.button("↓ Download", key=f"dl_{post['id']}", use_container_width=True):
            st.markdown(f"[Herunterladen]({post.get('url')})")

    # Kommentare dauerhaft sichtbar
    st.markdown('<div class="sep"></div>', unsafe_allow_html=True)
    st.markdown("**Kommentare**")

    # Kommentare laden (Server-Cache oder lokal)
    comments = get_comments(post["id"])
    if comments:
        for c in comments:
            st.markdown(f"- **{c.get('author','?')}**: {c.get('text')}")
    else:
        st.markdown("_Keine Kommentare_")

    # Formular zum Posten eines neuen Kommentars.
    # clear_on_submit=True leert das Eingabefeld nach erfolgreichem Submit
    # und vermeidet den SessionState-Fehler.
    with st.form(key=f"form_c_{post['id']}", clear_on_submit=True):
        new_text = st.text_area("Kommentar schreiben …", key=f"c_in_{post['id']}", height=80)
        submitted = st.form_submit_button("Posten", use_container_width=True)
        if submitted:
            text = (new_text or "").strip()
            if not text:
                st.warning("Bitte Text eingeben.")
            else:
                author = (st.session_state["user"] or {}).get("email", "Du")
                if add_comment(post["id"], text, author):
                    st.success("Kommentar gepostet")
                    _rerun()
                else:
                    st.error("Kommentar konnte nicht hinzugefügt werden")

    st.markdown("</div>", unsafe_allow_html=True)

def page_beitraege():
    """Hauptliste der Beiträge als zweispaltiges Grid."""
    top_hero()
    st.subheader("Beiträge")

    # Beiträge laden, wenn Cache leer
    if not st.session_state["beitraege"]:
        st.session_state["beitraege"] = api_beitraege()

    posts = st.session_state["beitraege"]
    if not posts:
        st.info("Noch keine Beiträge vorhanden.")
        return

    # Zweispaltiges Layout für Karten
    L, R = st.columns(2, gap="large")
    cols = [L, R]
    for i, p in enumerate(posts):
        with cols[i % 2]:
            render_post_card(p)

# ------------------------------------------------------------
# Sidebar + Routing
# ------------------------------------------------------------
with st.sidebar:
    st.subheader(APP_NAME)
    st.caption(f"Backend: {BACKEND_URL}")

    # Theme-Umschalter (zweiter Schalter in der Sidebar)
    label = "Dunkelmodus" if st.session_state["theme"] == "light" else "Hellmodus"
    if st.button(label, use_container_width=True, key="sidebar_theme"):
        st.session_state["theme"] = "dark" if st.session_state["theme"] == "light" else "light"
        _rerun()

    st.divider()
    if st.session_state["user"]:
        # Benutzerstatus + Logout
        st.markdown(f"Angemeldet als **{st.session_state['user'].get('email','?')}**")
        if st.button("Abmelden", use_container_width=True):
            st.session_state["user"] = None
            st.session_state["token"] = None
            st.session_state["beitraege"] = []
            _rerun()
        st.divider()
        # Navigation zwischen Beiträgen und Upload
        route = st.radio("Navigation", ["Beiträge", "Beitrag erstellen"], index=0)
    else:
        # Ohne Login nur Auth-Seite
        route = "auth"

# Routing-Logik basierend auf Login-Status und gewählter Route
if st.session_state["user"] is None or route == "auth":
    page_auth()
elif route == "Beiträge":
    page_beitraege()
else:
    page_upload()
