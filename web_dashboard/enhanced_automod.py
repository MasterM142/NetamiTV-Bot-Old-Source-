import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
import sqlite3
import json
import re

class EnhancedAutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.AUTO_MOD_CONFIG = {
            "banned_words": [
                "n1gg", "niger", "nigger", "n1gger",
                "NIGGER", "bitch", "bastard",
                "hurensohn", "hure", "fotze", "schlampe",
                "discord.gg/", "discord.com/invite/",
                "steamcommunity.com",
                "discordapp.com/invite"
            ],
            "spam_detection": {
                "max_duplicate_messages": 3,
                "time_window": 5
            },
            # Liste der User-IDs, die vom Anti-Spam ausgenommen sind
            "spam_exempt_users": [
                335774790554091520,  # Beispiel User ID
                1314739551603916890,
                1284213607390908487,
                862079163909144578,    # Beispiel User ID
                # Füge hier weitere User-IDs hinzu
            ]
        }
        self.user_message_history = {}
        self.init_database()

    def init_database(self):
        """Initialize the audit log database"""
        conn = sqlite3.connect('web_dashboard/audit_logs.db')
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

    def log_audit_event(self, user_id, username, discriminator, action_type, reason, 
                       message_content=None, channel_id=None, channel_name=None, 
                       guild_id=None, details=None, severity='medium'):
        """Log an audit event to the database"""
        try:
            conn = sqlite3.connect('web_dashboard/audit_logs.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO audit_logs 
                (user_id, username, discriminator, action_type, reason, message_content, 
                 channel_id, channel_name, guild_id, details, severity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (str(user_id), username, discriminator, action_type, reason, message_content,
                  str(channel_id) if channel_id else None, channel_name, str(guild_id) if guild_id else None, details, severity))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Fehler beim Loggen des Audit Events: {e}")

    def get_banned_word_details(self, content):
        """Get detailed information about which banned words were found"""
        found_words = []
        content_lower = content.lower()
        
        for word in self.AUTO_MOD_CONFIG["banned_words"]:
            if word.lower() in content_lower:
                # Find all occurrences with context
                pattern = re.compile(re.escape(word.lower()), re.IGNORECASE)
                matches = list(pattern.finditer(content))
                
                for match in matches:
                    start = max(0, match.start() - 10)
                    end = min(len(content), match.end() + 10)
                    context = content[start:end]
                    
                    found_words.append({
                        'word': word,
                        'position': match.start(),
                        'context': context,
                        'full_match': match.group()
                    })
        
        return found_words

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Check for banned words
        content = message.content
        banned_word_details = self.get_banned_word_details(content)
        
        if banned_word_details:
            await message.delete()
            
            # Create detailed log entry
            details_text = f"Gefundene verbotene Wörter: {len(banned_word_details)}\n"
            for detail in banned_word_details:
                details_text += f"- '{detail['word']}' an Position {detail['position']}: '{detail['context']}'\n"
            
            try:
                await message.author.ban(reason="AutoMod: Verwendung verbotener Wörter")
                action_taken = "Benutzer gebannt"
                
                try:
                    await message.author.send("⚠️ Du wurdest wegen der Verwendung verbotener Wörter gebannt.")
                except discord.HTTPException:
                    pass
                    
            except discord.HTTPException:
                action_taken = "Ban fehlgeschlagen - keine Berechtigung"

            # Log to database
            self.log_audit_event(
                user_id=message.author.id,
                username=message.author.name,
                discriminator=message.author.discriminator,
                action_type="word_filter",
                reason=f"Verwendung verbotener Wörter - {action_taken}",
                message_content=content,
                channel_id=message.channel.id,
                channel_name=message.channel.name,
                guild_id=message.guild.id if message.guild else None,
                details=details_text,
                severity="high"
            )

            # Log to Discord channel
            log_channel = discord.utils.get(message.guild.channels, name="mod-logs")
            if log_channel:
                embed = discord.Embed(
                    title="🛡️ AutoMod Action - Wort-Filter",
                    description=f"**Benutzer:** {message.author.mention} ({message.author.name}#{message.author.discriminator})\n"
                               f"**Aktion:** {action_taken}\n"
                               f"**Kanal:** {message.channel.mention}\n"
                               f"**Grund:** Verwendung verbotener Wörter",
                    color=discord.Color.red(),
                    timestamp=datetime.utcnow()
                )
                
                embed.add_field(
                    name="Nachrichteninhalt",
                    value=f"```{content[:1000]}{'...' if len(content) > 1000 else ''}```",
                    inline=False
                )
                
                embed.add_field(
                    name="Gefundene Wörter",
                    value=f"```{details_text[:1000]}{'...' if len(details_text) > 1000 else ''}```",
                    inline=False
                )
                
                await log_channel.send(embed=embed)

        # Spam Detection - Skip if user is exempt
        user_id = message.author.id
        
        # Prüfe ob der User vom Anti-Spam ausgenommen ist
        if user_id in self.AUTO_MOD_CONFIG["spam_exempt_users"]:
            return  # Skip spam detection for exempt users
            
        current_time = datetime.utcnow()
        
        if user_id not in self.user_message_history:
            self.user_message_history[user_id] = []
            
        self.user_message_history[user_id].append({
            'time': current_time,
            'content': content,
            'channel_id': message.channel.id
        })
        
        # Remove messages older than time window
        self.user_message_history[user_id] = [
            msg for msg in self.user_message_history[user_id]
            if (current_time - msg['time']).seconds <= self.AUTO_MOD_CONFIG["spam_detection"]["time_window"]
        ]
        
        if len(self.user_message_history[user_id]) >= self.AUTO_MOD_CONFIG["spam_detection"]["max_duplicate_messages"]:
            # Check if messages are similar (spam detection)
            recent_messages = self.user_message_history[user_id][-self.AUTO_MOD_CONFIG["spam_detection"]["max_duplicate_messages"]:]
            
            # Simple similarity check
            is_spam = True
            first_content = recent_messages[0]['content'].lower().strip()
            
            for msg in recent_messages[1:]:
                if msg['content'].lower().strip() != first_content:
                    is_spam = False
                    break
            
            if is_spam:
                try:
                    # Delete recent messages
                    deleted_count = 0
                    async for msg in message.channel.history(limit=50):
                        if msg.author.id == user_id and deleted_count < self.AUTO_MOD_CONFIG["spam_detection"]["max_duplicate_messages"]:
                            await msg.delete()
                            deleted_count += 1
                    
                    # Timeout user
                    await message.author.timeout(
                        discord.utils.utcnow() + timedelta(minutes=5), 
                        reason="AutoMod: Spam-Erkennung"
                    )
                    
                    action_taken = "Benutzer timeout (5 Minuten)"
                    
                    try:
                        await message.author.send("⚠️ Du wurdest wegen Spamming für 5 Minuten stummgeschaltet. Bitte warte, bevor du weitere Nachrichten sendest.")
                    except discord.HTTPException:
                        pass
                        
                except discord.HTTPException:
                    action_taken = "Timeout fehlgeschlagen - keine Berechtigung"

                # Create spam details
                spam_details = f"Spam-Nachrichten erkannt:\n"
                for i, msg in enumerate(recent_messages):
                    spam_details += f"{i+1}. '{msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}'\n"
                
                # Log to database
                self.log_audit_event(
                    user_id=message.author.id,
                    username=message.author.name,
                    discriminator=message.author.discriminator,
                    action_type="spam_detected",
                    reason=f"Spam-Erkennung - {action_taken}",
                    message_content=content,
                    channel_id=message.channel.id,
                    channel_name=message.channel.name,
                    guild_id=message.guild.id if message.guild else None,
                    details=spam_details,
                    severity="medium"
                )

                # Log to Discord channel
                log_channel = discord.utils.get(message.guild.channels, name="mod-logs")
                if log_channel:
                    embed = discord.Embed(
                        title="🛡️ AutoMod Action - Spam-Erkennung",
                        description=f"**Benutzer:** {message.author.mention} ({message.author.name}#{message.author.discriminator})\n"
                                   f"**Aktion:** {action_taken}\n"
                                   f"**Kanal:** {message.channel.mention}\n"
                                   f"**Grund:** Spam-Erkennung",
                        color=discord.Color.orange(),
                        timestamp=datetime.utcnow()
                    )
                    
                    embed.add_field(
                        name="Spam Details",
                        value=f"```{spam_details[:1000]}{'...' if len(spam_details) > 1000 else ''}```",
                        inline=False
                    )
                    
                    await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Log message deletions (not by automod)"""
        if message.author.bot:
            return
            
        # Check if this was deleted by automod (we can't easily detect this, so we'll skip recent automod actions)
        # This is a simple approach - in production you might want a more sophisticated method
        
        self.log_audit_event(
            user_id=message.author.id,
            username=message.author.name,
            discriminator=message.author.discriminator,
            action_type="message_deleted",
            reason="Nachricht gelöscht (nicht durch AutoMod)",
            message_content=message.content,
            channel_id=message.channel.id,
            channel_name=message.channel.name,
            guild_id=message.guild.id if message.guild else None,
            details=f"Nachricht gelöscht um {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            severity="low"
        )

    @commands.command(name="automod_stats")
    @commands.has_permissions(manage_messages=True)
    async def automod_stats(self, ctx):
        """Show automod statistics"""
        try:
            conn = sqlite3.connect('web_dashboard/audit_logs.db')
            cursor = conn.cursor()
            
            # Get statistics
            cursor.execute("SELECT COUNT(*) FROM audit_logs WHERE timestamp >= datetime('now', '-24 hours')")
            last_24h = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM audit_logs WHERE timestamp >= datetime('now', '-7 days')")
            last_7d = cursor.fetchone()[0]
            
            cursor.execute("SELECT action_type, COUNT(*) FROM audit_logs GROUP BY action_type")
            action_stats = cursor.fetchall()
            
            conn.close()
            
            embed = discord.Embed(
                title="📊 AutoMod Statistiken",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(name="Letzte 24 Stunden", value=str(last_24h), inline=True)
            embed.add_field(name="Letzte 7 Tage", value=str(last_7d), inline=True)
            embed.add_field(name="Web Dashboard", value="[Hier klicken](http://localhost:5000)", inline=True)
            
            if action_stats:
                stats_text = "\n".join([f"{action}: {count}" for action, count in action_stats])
                embed.add_field(name="Aktionen nach Typ", value=f"```{stats_text}```", inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"Fehler beim Abrufen der Statistiken: {e}")

async def setup(bot):
    await bot.add_cog(EnhancedAutoMod(bot))