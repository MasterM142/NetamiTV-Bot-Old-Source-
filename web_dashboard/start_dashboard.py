#!/usr/bin/env python3
"""
AutoMod Web Dashboard Starter
Dieses Skript startet das Web-Dashboard für den AutoMod Bot.
"""

import os
import sys
import subprocess

def check_requirements():
    """Check if all required packages are installed"""
    try:
        import flask
        import requests
        print("✓ Alle erforderlichen Pakete sind installiert")
        return True
    except ImportError as e:
        print(f"✗ Fehlende Abhängigkeit: {e}")
        print("Installiere die Abhängigkeiten mit: pip install -r requirements.txt")
        return False

def check_config():
    """Check if configuration is properly set up"""
    try:
        from config import DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, AUTHORIZED_USERS
        
        if DISCORD_CLIENT_ID == 'DEINE_DISCORD_CLIENT_ID_HIER':
            print("✗ Discord Client ID ist nicht konfiguriert")
            print("Bearbeite config.py und füge deine Discord-Anwendungsdaten ein")
            return False
            
        if DISCORD_CLIENT_SECRET == 'DEIN_DISCORD_CLIENT_SECRET_HIER':
            print("✗ Discord Client Secret ist nicht konfiguriert")
            print("Bearbeite config.py und füge deine Discord-Anwendungsdaten ein")
            return False
            
        if 'dein_discord_benutzername' in [user.lower() for user in AUTHORIZED_USERS]:
            print("⚠ Warnung: Standard-Benutzernamen in AUTHORIZED_USERS gefunden")
            print("Vergiss nicht, deine echten Discord-Benutzernamen in config.py einzutragen")
        
        print("✓ Konfiguration sieht gut aus")
        return True
        
    except ImportError:
        print("✗ config.py nicht gefunden")
        print("Kopiere config.py.example zu config.py und bearbeite die Einstellungen")
        return False

def main():
    print("🛡️  AutoMod Web Dashboard Starter")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("✗ app.py nicht gefunden. Stelle sicher, dass du im web_dashboard Ordner bist.")
        sys.exit(1)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check configuration
    if not check_config():
        sys.exit(1)
    
    print("\n🚀 Starte Web-Dashboard...")
    print("Dashboard wird verfügbar sein unter: http://neko.wisp.uno:12902")
    print("Drücke Ctrl+C zum Beenden")
    print("-" * 40)
    
    try:
        # Start the Flask app
        from app import app, init_database, DEBUG, HOST, PORT
        
        # Initialize database
        init_database()
        
        # Start the app
        app.run(debug=DEBUG, host=HOST, port=PORT)
        
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard beendet")
    except Exception as e:
        print(f"\n✗ Fehler beim Starten des Dashboards: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()