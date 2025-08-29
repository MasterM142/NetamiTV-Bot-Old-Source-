#!/usr/bin/env python3
"""
AutoMod Web Dashboard Setup
Dieses Skript hilft bei der initialen Einrichtung des Web-Dashboards.
"""

import os
import sys

def create_config():
    """Create configuration file with user input"""
    print("🔧 AutoMod Web Dashboard Setup")
    print("=" * 40)
    
    if os.path.exists('config.py'):
        overwrite = input("config.py existiert bereits. Überschreiben? (j/N): ").lower()
        if overwrite != 'j':
            print("Setup abgebrochen.")
            return
    
    print("\n📋 Discord-Anwendung Setup")
    print("1. Gehe zu: https://discord.com/developers/applications")
    print("2. Erstelle eine neue Anwendung")
    print("3. Gehe zu OAuth2 -> General")
    print("4. Füge 'http://neko.wisp.uno:12902/callback' zu den Redirect URIs hinzu")
    print("5. Kopiere Client ID und Client Secret\n")
    
    client_id = input("Discord Client ID: ").strip()
    if not client_id:
        print("Client ID ist erforderlich!")
        return
    
    client_secret = input("Discord Client Secret: ").strip()
    if not client_secret:
        print("Client Secret ist erforderlich!")
        return
    
    print("\n👥 Autorisierte Benutzer")
    print("Gib die Discord-Benutzernamen ein, die Zugriff haben sollen:")
    print("(Drücke Enter ohne Eingabe zum Beenden)")
    
    authorized_users = []
    while True:
        username = input(f"Benutzer {len(authorized_users) + 1}: ").strip()
        if not username:
            break
        authorized_users.append(username)
    
    if not authorized_users:
        print("Mindestens ein autorisierter Benutzer ist erforderlich!")
        return
    
    # Generate a random secret key
    import secrets
    secret_key = secrets.token_hex(32)
    
    # Create config.py
    config_content = f'''# Discord OAuth2 Configuration
# Automatisch generiert durch setup.py

DISCORD_CLIENT_ID = '{client_id}'
DISCORD_CLIENT_SECRET = '{client_secret}'
DISCORD_REDIRECT_URI = 'http://neko.wisp.uno:12902/callback'

# Autorisierte Discord-Benutzernamen (Groß-/Kleinschreibung wird ignoriert)
AUTHORIZED_USERS = {authorized_users}

# Flask-Konfiguration
SECRET_KEY = '{secret_key}'

# Server-Konfiguration
HOST = '0.0.0.0'  # Für lokalen Zugriff: 'localhost' oder '127.0.0.1'
PORT = 12902
DEBUG = True  # Setze auf False für Produktion
'''
    
    with open('config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"\n✅ config.py wurde erstellt!")
    print(f"   - Client ID: {client_id}")
    print(f"   - Autorisierte Benutzer: {', '.join(authorized_users)}")
    print(f"   - Server: http://neko.wisp.uno:12902")
    
    print(f"\n📝 Nächste Schritte:")
    print(f"1. Installiere Abhängigkeiten: pip install -r requirements.txt")
    print(f"2. Starte das Dashboard: python start_dashboard.py")
    print(f"3. Öffne http://neko.wisp.uno:12902 in deinem Browser")

def install_requirements():
    """Install required packages"""
    print("📦 Installiere Abhängigkeiten...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Abhängigkeiten erfolgreich installiert!")
            return True
        else:
            print(f"❌ Fehler bei der Installation: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Fehler bei der Installation: {e}")
        return False

def main():
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt nicht gefunden. Stelle sicher, dass du im web_dashboard Ordner bist.")
        sys.exit(1)
    
    print("Willkommen beim AutoMod Web Dashboard Setup!")
    print("\nWas möchtest du tun?")
    print("1. Konfiguration erstellen")
    print("2. Abhängigkeiten installieren")
    print("3. Beides")
    
    choice = input("\nWähle eine Option (1-3): ").strip()
    
    if choice in ['1', '3']:
        create_config()
    
    if choice in ['2', '3']:
        if not install_requirements():
            sys.exit(1)
    
    if choice == '3':
        print("\n🎉 Setup abgeschlossen!")
        print("Du kannst jetzt das Dashboard mit 'python start_dashboard.py' starten.")

if __name__ == '__main__':
    main()