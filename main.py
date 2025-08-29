import discord
from discord.ext import commands
from discord import app_commands
import os
import datetime
import asyncio
import json
import logging
from collections import defaultdict

# Configure logging to reduce spam
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Reduce discord.py logging verbosity
logging.getLogger('discord').setLevel(logging.WARNING)
logging.getLogger('discord.gateway').setLevel(logging.ERROR)

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.all(),
            application_id=""
        )
        # Alle Attribute vom ersten Bot
        self.points = {}
        self.temp_bans = {}
        self.custom_slowmodes = {}
        self.user_last_message = {}
        self.invite_tracker = defaultdict(dict)
        self.anti_nuke = defaultdict(lambda: {'actions': 0, 'last_reset': datetime.datetime.now()})
        self.raid_protection = {'enabled': False, 'account_age': 7, 'join_threshold': 10, 'join_window': 10}
        self.guild_id = 556552682865688603
        
        # Database semaphore to limit concurrent operations
        self.db_semaphore = asyncio.Semaphore(5)
        
        # AUTORISIERTE USER IDS - Hier deine User IDs eintragen
        self.authorized_users = [
            ,  # Deine User ID hier
            ,
            ,  # Weitere User ID hier
            # Weitere User IDs hier hinzufügen
        ]
        
        # COGS AUFGETEILT IN SPECIAL UND NORMAL
        self.special_extensions = [
            # Spezielle/Erweiterte Features
            'cogs.special.tickets',
            'cogs.special.tempvoice',  # Geändert von tempchannel zu tempvoice
            'cogs.special.reactionroles',
            'cogs.special.roleall',
            'cogs.special.screenrole',
            'cogs.special.streamplan',
            'cogs.special.website_monitor',
            'cogs.special.tempchannel',
            'cogs.special.web_dashboard',
        ]
        
        self.normal_extensions = [
            # Standard/Basis Features
            'cogs.normal.protection', 
            'cogs.normal.embed_handler',
            'cogs.normal.protected_users',
            'cogs.normal.automod',
            'cogs.normal.db',
            'cogs.normal.response_handler',
            'cogs.normal.moderation',
            'cogs.normal.review',
            'cogs.audit_logger',  # Comprehensive audit logging
        ]

    def is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized to use bot commands"""
        return user_id in self.authorized_users

    async def init_json_files(self):
        try:
            os.makedirs('data/users', exist_ok=True)
            os.makedirs('servers', exist_ok=True)
            
            if not os.path.exists('ticket_config.json'):
                ticket_config = {
                    "ticket_panels": {},
                    "active_tickets": {},
                    "statistics": {"total_tickets": 0}
                }
                with open('ticket_config.json', 'w') as f:
                    json.dump(ticket_config, f, indent=4)
                    
            if not os.path.exists('temp_voice.json'):
                temp_voice = {
                    'setup_channels': {},
                    'temp_channels': {},
                    'user_cooldowns': {},
                    'dm_sent_users': []
                }
                with open('temp_voice.json', 'w') as f:
                    json.dump(temp_voice, f, indent=4)
        except Exception as e:
            print(f"Error initializing JSON files: {e}")

    async def setup_hook(self):
        print("\n=== NETAMI COMBINED BOT SETUP ===")
        print("🔄 Starting setup...")
        
        try:
            await self.init_json_files()
            print("✅ JSON files initialized")
            
            await asyncio.sleep(1)  # Reduced sleep time
            
            # Clear commands with error handling
            try:
                self.tree.clear_commands(guild=None)
                await asyncio.sleep(0.5)
                await asyncio.wait_for(self.tree.sync(), timeout=30)
            except asyncio.TimeoutError:
                print("⚠️ Global command sync timed out")
            except Exception as e:
                print(f"⚠️ Global command sync failed: {e}")
            
            guild = discord.Object(id=self.guild_id)
            try:
                self.tree.clear_commands(guild=guild)
                await asyncio.sleep(0.5)
                await asyncio.wait_for(self.tree.sync(guild=guild), timeout=30)
            except asyncio.TimeoutError:
                print("⚠️ Guild command sync timed out")
            except Exception as e:
                print(f"⚠️ Guild command sync failed: {e}")
            
            print("✅ Commands cleared!")
            
            print("\n🔧 Loading NORMAL extensions...")
            for ext in self.normal_extensions:
                try:
                    await asyncio.wait_for(self.load_extension(ext), timeout=10)
                    await asyncio.sleep(0.5)  # Reduced sleep time
                    print(f"✅ Loaded: {ext}")
                except asyncio.TimeoutError:
                    print(f"⚠️ Timeout loading {ext}")
                except Exception as e:
                    print(f"❌ Failed to load {ext}: {e}")
            
            print("\n⭐ Loading SPECIAL extensions...")
            for ext in self.special_extensions:
                try:
                    await asyncio.wait_for(self.load_extension(ext), timeout=10)
                    await asyncio.sleep(0.5)  # Reduced sleep time
                    print(f"✅ Loaded: {ext}")
                except asyncio.TimeoutError:
                    print(f"⚠️ Timeout loading {ext}")
                except Exception as e:
                    print(f"❌ Failed to load {ext}: {e}")
            
            await asyncio.sleep(1)
            try:
                self.tree.copy_global_to(guild=guild)
                await asyncio.sleep(0.5)
                await asyncio.wait_for(self.tree.sync(guild=guild), timeout=30)
                print(f"✅ Commands synced to guild ID: {self.guild_id}")
            except asyncio.TimeoutError:
                print("⚠️ Final guild sync timed out")
            except Exception as e:
                print(f"⚠️ Final guild sync failed: {e}")
                
            print("=== COMBINED BOT SETUP COMPLETE ===\n")
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")

    async def on_ready(self):
        print(f"\n✅ NETAMI COMBINED BOT is online! Logged in as {self.user}")
        try:
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name="rawr~"
                )
            )
        except Exception as e:
            print(f"⚠️ Failed to set presence: {e}")

    async def on_error(self, event, *args, **kwargs):
        """Handle errors to prevent crashes"""
        print(f"Error in event {event}: {args}")

    async def close(self):
        """Properly close the bot"""
        print("🔄 Shutting down bot...")
        await super().close()

async def main():
    bot = Bot()
    
    try:
        # Add timeout for bot operations
        await asyncio.wait_for(
            bot.start(''),
            timeout=None  # No timeout for main connection
        )
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot crashed: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Program interrupted")
    except Exception as e:
        print(f"❌ Program crashed: {e}")
