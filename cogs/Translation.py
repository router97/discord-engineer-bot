import json
import os

import discord
from discord.ext import commands
import langcodes

from bot import translator


class Translation(commands.Cog):
    """Translation description."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.hybrid_command(name="translate", description="Translate a message.")
    async def translate(self, ctx: commands.Context, *, message: str = commands.parameter(description="The message you want to translate.", displayed_name="Message")):
        file_path = "data/users.json"
        
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, "r", encoding="utf-8") as fl:
                all_dict = json.load(fl)
        else:
            all_dict = {}
        
        user_key = str(ctx.author.id)
            
        if user_key not in all_dict:
            all_dict[user_key] = {}
        
        language_code = all_dict[user_key].get('lang', 'en')
        
        embed = discord.Embed(color=discord.Color.red(), description=translator.translate(message, dest=language_code).text)
        
        await ctx.reply(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name="setlang", description="Set a language to translate to.")
    async def setlang(self, ctx: commands.Context, language: str = commands.parameter(default="en", description="The language you wish to translate to.", displayed_default="English", displayed_name="Language")):
        """Set a language to translate to."""
        
        try:
            lang_obj = langcodes.Language.get(language.casefold())
            if not lang_obj.is_valid():
                raise ValueError("Invalid language code or name")
            language_code = lang_obj.language
            language_name = lang_obj.display_name()
        except ValueError:
            await ctx.reply(f'Invalid language: {language}.', ephemeral=True)
            return
        
        file_path = "data/users.json"
        
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, "r", encoding="utf-8") as fl:
                all_dict = json.load(fl)
        else:
            all_dict = {}
        
        user_key = str(ctx.author.id)
        
        if user_key not in all_dict:
            all_dict[user_key] = {}
        
        all_dict[user_key]['lang'] = language_code

        
        with open(file_path, "w", encoding="utf-8") as fl:
            json.dump(all_dict, fl, indent=4)
        
        await ctx.reply(f'Changed your language to {language}', ephemeral=True)

# SETUP
def setup(bot: commands.Bot):
    bot.add_cog(Translation(bot))