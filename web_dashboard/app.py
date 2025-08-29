from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from flask_session import Session
import requests
import os
from datetime import datetime, timedelta
import sqlite3
import json
from functools import wraps

# Import configuration
try:
    from config import *
except ImportError:
    # Fallback configuration if config.py doesn't exist
    DISCORD_CLIENT_ID = 'YOUR_DISCORD_CLIENT_ID'
    DISCORD_CLIENT_SECRET = 'YOUR_DISCORD_CLIENT_SECRET'
    DISCORD_REDIRECT_URI = 'http://neko.wisp.uno:12902/callback'
    AUTHORIZED_USERS = ['your_discord_username']
    SECRET_KEY = 'change-this-secret-key'
    HOST = '0.0.0.0'
    PORT = 12902
    DEBUG = True

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

DISCORD_API_ENDPOINT = 'https://discord.com/api/v10'

def init_database():
    """Initialize the audit log database"""
    conn = sqlite3.connect('audit_logs.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
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
        )
    ''')
    
    conn.commit()
    conn.close()

def log_audit_event(user_id, username, discriminator, action_type, reason, 
                   message_content=None, channel_id=None, channel_name=None, 
                   guild_id=None, details=None, severity='medium'):
    """Log an audit event to the database"""
    conn = sqlite3.connect('audit_logs.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO audit_logs 
        (user_id, username, discriminator, action_type, reason, message_content, 
         channel_id, channel_name, guild_id, details, severity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, username, discriminator, action_type, reason, message_content,
          channel_id, channel_name, guild_id, details, severity))
    
    conn.commit()
    conn.close()

def require_auth(f):
    """Decorator to require Discord authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'discord_user' not in session:
            return redirect(url_for('login'))
        
        # Check if user is authorized
        discord_user = session['discord_user']
        username = discord_user.get('username', '').lower()
        
        if username not in [user.lower() for user in AUTHORIZED_USERS]:
            return render_template('unauthorized.html', username=username)
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'discord_user' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login')
def login():
    discord_login_url = f"{DISCORD_API_ENDPOINT}/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify"
    return redirect(discord_login_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    
    if not code:
        return redirect(url_for('index'))
    
    # Exchange code for access token
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    response = requests.post(f"{DISCORD_API_ENDPOINT}/oauth2/token", data=data, headers=headers)
    
    if response.status_code != 200:
        return redirect(url_for('index'))
    
    token_data = response.json()
    access_token = token_data['access_token']
    
    # Get user information
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    
    user_response = requests.get(f"{DISCORD_API_ENDPOINT}/users/@me", headers=headers)
    
    if user_response.status_code != 200:
        return redirect(url_for('index'))
    
    user_data = user_response.json()
    session['discord_user'] = user_data
    
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@require_auth
def dashboard():
    # Get recent audit logs
    conn = sqlite3.connect('audit_logs.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM audit_logs 
        ORDER BY timestamp DESC 
        LIMIT 50
    ''')
    
    logs = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries for easier template handling
    log_list = []
    for log in logs:
        log_dict = {
            'id': log[0],
            'timestamp': log[1],
            'user_id': log[2],
            'username': log[3],
            'discriminator': log[4],
            'action_type': log[5],
            'reason': log[6],
            'message_content': log[7],
            'channel_id': log[8],
            'channel_name': log[9],
            'guild_id': log[10],
            'details': log[11],
            'severity': log[12]
        }
        log_list.append(log_dict)
    
    return render_template('dashboard.html', logs=log_list, user=session['discord_user'])

@app.route('/api/logs')
@require_auth
def api_logs():
    """API endpoint to get logs with filtering"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 25))
    action_type = request.args.get('action_type', '')
    severity = request.args.get('severity', '')
    user_search = request.args.get('user_search', '')
    category = request.args.get('category', 'all')
    
    conn = sqlite3.connect('audit_logs.db')
    cursor = conn.cursor()
    
    # Build query with filters
    query = "SELECT * FROM audit_logs WHERE 1=1"
    params = []
    
    # Category filtering
    if category == 'bot':
        bot_actions = ['ticket_created', 'ticket_closed', 'temp_channel_created', 'temp_channel_deleted', 'automod_action']
        query += f" AND action_type IN ({','.join(['?' for _ in bot_actions])})"
        params.extend(bot_actions)
    elif category == 'moderation':
        mod_actions = ['user_banned', 'user_kicked', 'user_timeout', 'message_deleted', 'spam_detected', 'word_filter']
        query += f" AND action_type IN ({','.join(['?' for _ in mod_actions])})"
        params.extend(mod_actions)
    elif category == 'server':
        server_actions = ['member_joined', 'member_left', 'role_added', 'role_removed', 'channel_created', 'channel_deleted', 'channel_updated', 'server_updated']
        query += f" AND action_type IN ({','.join(['?' for _ in server_actions])})"
        params.extend(server_actions)
    
    if action_type:
        query += " AND action_type = ?"
        params.append(action_type)
    
    if severity:
        query += " AND severity = ?"
        params.append(severity)
    
    if user_search:
        query += " AND (username LIKE ? OR user_id LIKE ?)"
        params.extend([f"%{user_search}%", f"%{user_search}%"])
    
    query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
    params.extend([per_page, (page - 1) * per_page])
    
    cursor.execute(query, params)
    logs = cursor.fetchall()
    
    # Get total count for pagination
    count_query = query.replace("SELECT *", "SELECT COUNT(*)").split("ORDER BY")[0]
    cursor.execute(count_query, params[:-2])  # Remove LIMIT and OFFSET params
    total_count = cursor.fetchone()[0]
    
    conn.close()
    
    # Convert to list of dictionaries
    log_list = []
    for log in logs:
        log_dict = {
            'id': log[0],
            'timestamp': log[1],
            'user_id': log[2],
            'username': log[3],
            'discriminator': log[4],
            'action_type': log[5],
            'reason': log[6],
            'message_content': log[7],
            'channel_id': log[8],
            'channel_name': log[9],
            'guild_id': log[10],
            'details': log[11],
            'severity': log[12]
        }
        log_list.append(log_dict)
    
    return jsonify({
        'logs': log_list,
        'total': total_count,
        'page': page,
        'per_page': per_page,
        'total_pages': (total_count + per_page - 1) // per_page
    })

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_database()
    app.run(debug=DEBUG, host=HOST, port=PORT)