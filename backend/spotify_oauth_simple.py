"""
Script simple para obtener el Refresh Token de Spotify usando ngrok
"""

import requests
from urllib.parse import urlencode
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys

# ⚠️ Configura esto con tus credenciales
CLIENT_ID = "51ce072da9c24789ae732edf00428af1"
CLIENT_SECRET = "ddaea4e7dfa4428ca0ab97a877117444"

# ⚠️ REDIRECT_URI debe ser la URL pública de ngrok + /callback
REDIRECT_URI = "https://semiannually-unequiangular-adelle.ngrok-free.dev/callback"

# Scopes que necesitas
SCOPES = "playlist-modify-public playlist-modify-private"

# Variable global para almacenar el código temporal
code = None

# -------------------------------
# Servidor HTTP simple para recibir callback
# -------------------------------
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global code
        if "?code=" in self.path:
            code = self.path.split("?code=")[1].split("&")[0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()

            html = """
            <html>
            <body style="font-family: Arial; text-align: center; padding: 50px; background: #1DB954; color: white;">
                <h1>✅ ¡Éxito! Cierra esta ventana</h1>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))

    def log_message(self, *args):
        # Desactiva logs por cada request
        pass

# -------------------------------
# Flujo de autorización
# -------------------------------
print("="*60)
print("🎵 SPOTIFY OAUTH - USANDO NGROK")
print("="*60)
print("\n1. Se abrirá tu navegador")
print("2. Acepta los permisos de Spotify")
print("\nPresiona ENTER para continuar...")
input()

# Construir URL de autorización
params = {
    'client_id': CLIENT_ID,
    'response_type': 'code',
    'redirect_uri': REDIRECT_URI,
    'scope': SCOPES,
    'show_dialog': 'true'
}
url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
webbrowser.open(url)
print("\n🔄 Esperando autorización...")
print("URL de autorización:", url)

# Ejecutar servidor HTTP local
server = HTTPServer(('localhost', 8888), Handler)
server.handle_request()

if not code:
    print("❌ No se recibió el código")
    sys.exit(1)

print("✅ Código recibido! Obteniendo refresh token...")

# -------------------------------
# Intercambio de código por refresh token
# -------------------------------
data = {
    'grant_type': 'authorization_code',
    'code': code,
    'redirect_uri': REDIRECT_URI,
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET
}

resp = requests.post("https://accounts.spotify.com/api/token", data=data)

if resp.status_code == 200:
    refresh_token = resp.json().get("refresh_token")
    print("\n" + "="*60)
    print("✅ ¡ÉXITO! Añade esto a tu archivo .env:")
    print("="*60)
    print(f"\nSPOTIFY_REFRESH_TOKEN={refresh_token}\n")
    print("="*60)
else:
    print(f"❌ Error al obtener token: {resp.status_code}")
    print(resp.text)
