"""
Fun
===

This cog module contains miscellaneous commands, mostly without actual purpose.
"""

import datetime
import time
from random import randint, choice

import discord
from discord.ext import commands


class Fun(commands.Cog):
    """Miscellaneous commands"""
    
    emojis_num = ('1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟')
    fakt_map = {
        'a': 'ф', 'b': 'и', 'c': 'с', 'd': 'в', 'e': 'у', 'f': 'а', 'g': 'п', 'h': 'р',
        'i': 'ш', 'j': 'о', 'k': 'л', 'l': 'д', 'm': 'ь', 'n': 'т', 'o': 'щ', 'p': 'з',
        'q': 'й', 'r': 'к', 's': 'ы', 't': 'е', 'u': 'г', 'v': 'м', 'w': 'ц', 'x': 'ч',
        'y': 'н', 'z': 'я', ',': 'б', '.': 'ю', '[': 'х', ']': 'ъ', "'": 'э', '`': 'ё',
        ' ': ' '
    }
    random_replies = [
        "I'm good", 
        "KYS = Keep Yourself Safe", 
        "Nah", 
        "I'll pass on that one", 
        "No, thanks", 
        "/me Лицом к стене! 1... 2... 3... Стреляю!"
    ]
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.hybrid_command(name="ip", description="Generate a random IP address")
    async def ip(self, ctx: commands.Context):
        """Generate a random IP address"""
        await ctx.reply('.'.join(str(randint(0,255)) for _ in range(4)))
    
    @commands.hybrid_command(name="fog", description="the fog is coming.")
    async def fog(self, ctx: commands.Context):
        """The fog is coming"""
        current_time = time.time()
        fog_time = datetime.datetime(2026, 4, 7).timestamp()
        time_difference = fog_time - current_time
        remaining_time = datetime.timedelta(seconds=time_difference)
        await ctx.reply(f'{remaining_time.days} days {round(remaining_time.seconds / 3600)} hours remaining...')
    
    @commands.hybrid_command(name="kys", description="Generate a random reply")
    async def kys(self, ctx: commands.Context):
        """Generate a random reply"""
        await ctx.reply(choice(self.random_replies))
    
    @commands.command(name='do', description='Change the presence of the bot.')
    async def do(self, ctx: commands.Context, *, activity: str):
        """
        # Example:
            **User:** ".do Team Fortress 2"
            *Bot's presence became: "Playing Team Fortress 2"*
        """
        
        # Create Activity object
        new_presence = discord.Activity(type=discord.ActivityType.playing, name=activity)
        
        # Change the presence
        await self.bot.change_presence(activity=new_presence, status=discord.Status.do_not_disturb)
        
        # Acknowledge the action
        await ctx.reply('changed the presence!', ephemeral=True)
    
    async def cog_command_error(self, ctx: commands.Context, error):
        await ctx.send_help(ctx.command)
        print(repr(error))


def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))