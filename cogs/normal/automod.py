import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta

class AutoMod(commands.Cog):
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

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Check for banned words
        content = message.content.lower()
        if any(word in content for word in self.AUTO_MOD_CONFIG["banned_words"]):
            await message.delete()
            try:
                await message.author.ban(reason="AutoMod: Use of banned words")
                await message.author.send("⚠️ You have been banned for using prohibited words.")
            except discord.HTTPException:
                pass

            # Log the violation
            log_channel = discord.utils.get(message.guild.channels, name="mod-logs")
            if log_channel:
                embed = discord.Embed(
                    title="🛡️ AutoMod Action",
                    description=f"User: {message.author.mention}\nAction: Message Deleted + Ban\nReason: Prohibited Content",
                    color=discord.Color.red(),
                    timestamp=datetime.utcnow()
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
            
        self.user_message_history[user_id].append(current_time)
        
        # Remove messages older than time window
        self.user_message_history[user_id] = [
            msg_time for msg_time in self.user_message_history[user_id]
            if (current_time - msg_time).seconds <= self.AUTO_MOD_CONFIG["spam_detection"]["time_window"]
        ]
        
        if len(self.user_message_history[user_id]) >= self.AUTO_MOD_CONFIG["spam_detection"]["max_duplicate_messages"]:
            try:
                await message.channel.purge(
                    limit=self.AUTO_MOD_CONFIG["spam_detection"]["max_duplicate_messages"],
                    check=lambda m: m.author.id == user_id
                )
                await message.author.timeout(discord.utils.utcnow() + timedelta(minutes=5), reason="AutoMod: Spam detection")
                await message.author.send("⚠️ You have been timed out for spamming. Please wait before sending more messages.")
            except discord.HTTPException:
                pass

async def setup(bot):
    await bot.add_cog(AutoMod(bot))