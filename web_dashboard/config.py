# Discord OAuth2 Configuration
# Du musst eine Discord-Anwendung erstellen unter: https://discord.com/developers/applications

# Schritt 1: Gehe zu https://discord.com/developers/applications
# Schritt 2: Klicke auf "New Application" und gib einen Namen ein
# Schritt 3: Gehe zu "OAuth2" -> "General"
# Schritt 4: Kopiere die "Client ID" und "Client Secret"
# Schritt 5: Füge "http://neko.wisp.uno:12902/callback" zu den Redirect URIs hinzu

DISCORD_CLIENT_ID = 'DEINE_DISCORD_CLIENT_ID_HIER'
DISCORD_CLIENT_SECRET = 'DEIN_DISCORD_CLIENT_SECRET_HIER'
DISCORD_REDIRECT_URI = 'http://neko.wisp.uno:12902/callback'

# Autorisierte Discord-Benutzernamen (Groß-/Kleinschreibung wird ignoriert)
# Nur diese Benutzer können auf das Dashboard zugreifen
AUTHORIZED_USERS = [
    'dein_discord_benutzername',  # Ersetze mit echten Discord-Benutzernamen
    'admin_benutzername',
    'moderator_benutzername'
]

# Flask-Konfiguration
SECRET_KEY = 'dein-geheimer-schluessel-hier-aendern'  # Ändere dies zu einem sicheren Schlüssel

# Server-Konfiguration
HOST = '0.0.0.0'  # Für lokalen Zugriff: 'localhost' oder '127.0.0.1'
PORT = 12902
DEBUG = True  # Setze auf False für Produktion