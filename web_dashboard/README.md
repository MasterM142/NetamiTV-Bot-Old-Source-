# AutoMod Web Dashboard

Ein detailliertes Web-Dashboard für Discord AutoMod mit OAuth2-Authentifizierung und erweiterten Audit-Logs.

## Features

- 🔐 **Discord OAuth2 Authentifizierung** - Sichere Anmeldung mit Discord
- 📊 **Detaillierte Audit-Logs** - Vollständige Nachrichteninhalte und Kontext
- 🔍 **Erweiterte Filterung** - Nach Aktion, Schweregrad und Benutzer filtern
- 📱 **Responsive Design** - Funktioniert auf Desktop und Mobile
- ⚡ **Echtzeit-Updates** - Automatische Aktualisierung alle 30 Sekunden
- 📈 **Statistiken** - Übersicht über Moderationsaktivitäten

## Installation

### 1. Discord-Anwendung erstellen

1. Gehe zu [Discord Developer Portal](https://discord.com/developers/applications)
2. Klicke auf "New Application" und gib einen Namen ein
3. Gehe zu "OAuth2" -> "General"
4. Kopiere die "Client ID" und "Client Secret"
5. Füge `http://neko.wisp.uno:12902/callback` zu den Redirect URIs hinzu

### 2. Abhängigkeiten installieren

```bash
cd web_dashboard
pip install -r requirements.txt
```

### 3. Konfiguration

Bearbeite `config.py` und füge deine Discord-Anwendungsdaten ein:

```python
DISCORD_CLIENT_ID = 'deine_client_id'
DISCORD_CLIENT_SECRET = 'dein_client_secret'

AUTHORIZED_USERS = [
    'dein_discord_benutzername',
    'admin_benutzername'
]
```

### 4. Enhanced AutoMod aktivieren

Ersetze die normale AutoMod-Cog mit der erweiterten Version:

1. Kopiere `enhanced_automod.py` nach `cogs/normal/automod.py`
2. Oder lade die erweiterte Version in deinem Bot:

```python
# In deiner main.py oder bot.py
await bot.load_extension('web_dashboard.enhanced_automod')
```

### 5. Web-Dashboard starten

```bash
cd web_dashboard
python app.py
```

Das Dashboard ist dann unter `http://neko.wisp.uno:12902` erreichbar.

## Verwendung

### Anmeldung

1. Gehe zu `http://neko.wisp.uno:12902`
2. Klicke auf "Mit Discord anmelden"
3. Autorisiere die Anwendung
4. Du wirst zum Dashboard weitergeleitet (nur wenn du autorisiert bist)

### Dashboard-Features

#### Audit-Logs
- **Vollständige Nachrichteninhalte** - Sieh genau, was geschrieben wurde
- **Benutzerinformationen** - Username, Discriminator und User-ID
- **Kanal-Details** - Kanalname und ID
- **Zeitstempel** - Genaue Zeit der Aktion
- **Schweregrad** - Hoch, Mittel, Niedrig
- **Detaillierte Gründe** - Warum die Aktion ausgeführt wurde

#### Filterung
- **Nach Aktion** - Nachricht gelöscht, Benutzer gebannt, etc.
- **Nach Schweregrad** - Hoch, Mittel, Niedrig
- **Nach Benutzer** - Suche nach Username oder User-ID

#### Statistiken
- Anzahl der Aktionen nach Schweregrad
- Gesamtanzahl der Einträge
- Echtzeit-Updates

## AutoMod-Aktionen

### Wort-Filter
- Erkennt verbotene Wörter in Nachrichten
- Zeigt **genau welche Wörter** gefunden wurden
- Zeigt **Kontext** um die Wörter herum
- Zeigt **Position** der Wörter in der Nachricht
- **Schweregrad**: Hoch

### Spam-Erkennung
- Erkennt wiederholte identische Nachrichten
- Zeigt alle **Spam-Nachrichten** im Detail
- Timeout für 5 Minuten
- **Schweregrad**: Mittel

### Nachrichtenlöschung
- Protokolliert gelöschte Nachrichten
- Zeigt **vollständigen Nachrichteninhalt**
- **Schweregrad**: Niedrig

## Konfiguration

### Autorisierte Benutzer

Nur Benutzer in der `AUTHORIZED_USERS`-Liste können auf das Dashboard zugreifen:

```python
AUTHORIZED_USERS = [
    'dein_username',
    'moderator_username',
    'admin_username'
]
```

### AutoMod-Einstellungen

In `enhanced_automod.py` kannst du folgende Einstellungen anpassen:

```python
AUTO_MOD_CONFIG = {
    "banned_words": [
        # Füge hier verbotene Wörter hinzu
    ],
    "spam_detection": {
        "max_duplicate_messages": 3,  # Anzahl identischer Nachrichten
        "time_window": 5  # Zeitfenster in Sekunden
    },
    "spam_exempt_users": [
        # User-IDs, die vom Spam-Schutz ausgenommen sind
    ]
}
```

## Sicherheit

- **OAuth2-Authentifizierung** - Sichere Discord-Anmeldung
- **Autorisierungsprüfung** - Nur autorisierte Benutzer haben Zugriff
- **Session-Management** - Sichere Session-Verwaltung
- **SQL-Injection-Schutz** - Parametrisierte Datenbankabfragen

## Troubleshooting

### "Nicht autorisiert" Fehler
- Überprüfe, ob dein Discord-Username in `AUTHORIZED_USERS` steht
- Achte auf Groß-/Kleinschreibung (wird automatisch ignoriert)

### Discord OAuth Fehler
- Überprüfe Client ID und Client Secret
- Stelle sicher, dass die Redirect URI korrekt ist
- Überprüfe, ob die Discord-Anwendung korrekt konfiguriert ist

### Datenbank-Fehler
- Stelle sicher, dass der `web_dashboard` Ordner existiert
- Die Datenbank wird automatisch erstellt beim ersten Start

### Logs werden nicht angezeigt
- Stelle sicher, dass `enhanced_automod.py` geladen ist
- Überprüfe, ob AutoMod-Aktionen stattfinden
- Schaue in die Konsole nach Fehlermeldungen

## Entwicklung

### Neue Features hinzufügen

1. **Neue AutoMod-Regel**: Erweitere `enhanced_automod.py`
2. **Neue Dashboard-Seite**: Erstelle neue HTML-Templates
3. **API-Endpunkte**: Füge neue Routen in `app.py` hinzu

### Datenbank-Schema

```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id TEXT NOT NULL,
    username TEXT NOT NULL,
    discriminator TEXT,
    action_type TEXT NOT NULL,
    reason TEXT,
    message_content TEXT,
    channel_id TEXT,
    channel_name TEXT,
    guild_id TEXT,
    details TEXT,
    severity TEXT DEFAULT 'medium'
);
```

## Support

Bei Problemen oder Fragen:
1. Überprüfe die Konsole auf Fehlermeldungen
2. Stelle sicher, dass alle Abhängigkeiten installiert sind
3. Überprüfe die Discord-Anwendungskonfiguration