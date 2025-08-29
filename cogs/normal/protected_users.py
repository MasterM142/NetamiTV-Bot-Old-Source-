import discord
from discord.ext import commands
import datetime

class ProtectedUsers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_handler = bot.get_cog('EmbedHandler')
        self.protected_user_ids = [
            ,
            ,
            ,
            
        ]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Check if message contains @ and if it's for a protected user
        for user_id in self.protected_user_ids:
            if f"<@{user_id}>" in message.content or f"<@!{user_id}>" in message.content:
                if message.guild.me.guild_permissions.moderate_members and message.guild.me.top_role > message.author.top_role:
                    try:
                        await message.delete()
                        await message.author.timeout(
                            datetime.timedelta(minutes=30),
                            reason="Mentioning protected users"
                        )
                        
                        # Fix for missing emojis attribute
                        if self.embed_handler and hasattr(self.embed_handler, 'emojis'):
                            fail_emoji = self.embed_handler.emojis.FAIL
                        else:
                            fail_emoji = "❌"  # Fallback emoji
                        
                        await message.channel.send(f"{fail_emoji} - {message.author.mention} has been timed out for 30 minutes for pinging a protected user.")
                        
                        try:
                            await message.author.send("You have been timed out for 30 minutes for pinging a protected user.")
                        except:
                            pass
                            
                    except discord.HTTPException:
                        # Fix for missing emojis attribute in error handling too
                        if self.embed_handler and hasattr(self.embed_handler, 'emojis'):
                            fail_emoji = self.embed_handler.emojis.FAIL
                        else:
                            fail_emoji = "❌"  # Fallback emoji
                            
                        await message.channel.send(f"{fail_emoji} - Failed to timeout {message.author.mention}")

async def setup(bot):
    await bot.add_cog(ProtectedUsers(bot))
