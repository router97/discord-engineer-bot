import discord
from discord import app_commands
from discord.ext import commands
import langcodes

from bot import translator, bot
from utilities import ensure_user_is_in_database, ensure_user_is_in_database_interaction


class Translation(commands.Cog):
    """Translation description."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.hybrid_command(name="translate", description="Translate a message.")
    @ensure_user_is_in_database()
    async def translate(self, ctx: commands.Context, *, message: str = commands.parameter(description="The message you want to translate.", displayed_name="Message")):
        
        translate_to = await ctx.bot.db.fetchval('SELECT translate_to FROM users WHERE id = $1', ctx.author.id)
        translate_to = langcodes.standardize_tag(translate_to)
        
        translated_text = translator.translate(text=message, dest=translate_to, src='auto')
    
        embed = discord.Embed(
            color=discord.Color.red(), 
            title=f'{langcodes.get(translated_text.src).display_name()} -> {langcodes.get(translated_text.dest).display_name()}', 
            description=f'*{translated_text.text}*', 
        )
    
        await ctx.reply(embed=embed, ephemeral=True, silent=True, delete_after=60.0)
    
    @commands.hybrid_command(name="setlang", description="Set your preferred language for translation.")
    @ensure_user_is_in_database()
    async def setlang(self, ctx: commands.Context, language: str = commands.parameter(default="en", description="The language you wish to translate to.", displayed_default="English", displayed_name="Language")):
        try:
            new_language = langcodes.get(language.casefold())
            if not new_language.is_valid():
                raise ValueError("Invalid language code or name")
            language_code = new_language.to_alpha3()
        except ValueError:
            embed = discord.Embed(
                title="Error!",
                description=f'**Invalid language:** *{language}*',
                color=discord.Color.red(), 
            )
            await ctx.reply(embed=embed, delete_after=60.0, ephemeral=True, silent=True)
            await ctx.message.delete()
            return
        
        old_language = await bot.db.fetchval('SELECT translate_to FROM users WHERE id = $1', ctx.author.id)
        old_language = langcodes.get(old_language)
        
        if old_language.to_alpha3() == new_language.to_alpha3():
            embed = discord.Embed(
                title="Language already set!",
                description=f'*{new_language.display_name()}* is already set.',
                color=discord.Color.teal(), 
            )
            await ctx.reply(embed=embed, delete_after=60.0, ephemeral=True, silent=True)
            await ctx.message.delete()
            return
            
        await bot.db.execute('UPDATE users SET translate_to = $2 WHERE id = $1', ctx.author.id, language_code)
        
        embed = discord.Embed(
            title="Language Preference Updated!",
            description=f'**{old_language.display_name()}** -> **{new_language.display_name()}**',
            color=discord.Color.green(), 
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        
        await ctx.reply(embed=embed, delete_after=60.0, ephemeral=True, silent=True)
        await ctx.message.delete()

@app_commands.context_menu(name='Translate')
@ensure_user_is_in_database_interaction()
async def translate_message_context_menu(interaction: discord.Interaction, message: discord.Message):
    translate_to = await bot.db.fetchval('SELECT translate_to FROM users WHERE id = $1', interaction.user.id)
    translate_to = langcodes.standardize_tag(translate_to)
    
    translated_text = translator.translate(text=message.content, dest=translate_to, src='auto')
    
    embed = discord.Embed(
        color=discord.Color.red(), 
        title=f'{langcodes.get(translated_text.src).display_name()} -> {langcodes.get(translated_text.dest).display_name()}', 
        description=f'*{translated_text.text}*', 
        timestamp=message.created_at, 
    )
    embed.set_footer(text=message.author.display_name, icon_url=message.author.display_avatar.url)
    
    await interaction.response.send_message(embed=embed, ephemeral=True, silent=True, delete_after=60.0)

bot.tree.add_command(translate_message_context_menu)

# SETUP
def setup(bot: commands.Bot):
    bot.add_cog(Translation(bot))