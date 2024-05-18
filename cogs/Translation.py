import json
import os

import discord
from discord import app_commands
from discord.ext import commands
import langcodes

from bot import translator, bot
from utilities import ensure_user_is_in_database

class Translation(commands.Cog):
    """Translation description."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.hybrid_command(name="translate", description="Translate a message.")
    async def translate(self, ctx: commands.Context, *, message: str = commands.parameter(description="The message you want to translate.", displayed_name="Message")):
        
        translate_to = await ctx.bot.db.fetchval('SELECT translate_to FROM users WHERE user_id = $1', ctx.author.id)
        translate_to = langcodes.standardize_tag(translate_to)
        
        embed = discord.Embed(color=discord.Color.red(), description=translator.translate(message, dest=translate_to).text)
        
        await ctx.reply(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name="setlang", description="Set a language to translate to.")
    @ensure_user_is_in_database()
    async def setlang(self, ctx: commands.Context, language: str = commands.parameter(default="en", description="The language you wish to translate to.", displayed_default="English", displayed_name="Language")):
        """Set a language to translate to."""
        
        try:
            lang_obj = langcodes.Language.get(language.casefold())
            if not lang_obj.is_valid():
                raise ValueError("Invalid language code or name")
            language_code = lang_obj.to_alpha3()
        except ValueError:
            await ctx.reply(f'Invalid language: {language}.', ephemeral=True)
            return
        
        
        await bot.db.execute('UPDATE users SET translate_to = $2 WHERE user_id = $1', ctx.author.id, language_code)
        
        
        await ctx.reply(f'Changed your language to {lang_obj.display_name()}', ephemeral=True)

@app_commands.context_menu(name='Translate')
async def translate_message_context_menu(interaction: discord.Interaction, message: discord.Message):
    
    translate_to = await bot.db.fetchval('SELECT translate_to FROM users WHERE user_id = $1', interaction.user.id)
    translate_to = langcodes.standardize_tag(translate_to)
    
    embed = discord.Embed(color=discord.Color.red(), description=translator.translate(message.content, dest=translate_to).text)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

bot.tree.add_command(translate_message_context_menu)

# SETUP
def setup(bot: commands.Bot):
    bot.add_cog(Translation(bot))