"""
Translation
===========

This cog module contains commands that help with localization and translation.
"""
import discord
from discord import app_commands
from discord.ext import commands

import langcodes
from googletrans import Translator, LANGUAGES
from googletrans.models import Translated

from utilities.db.decorators import ensure_user_is_in_database, ensure_user_is_in_database_interaction
from converters.language import Language

translator: Translator = Translator()
"""
A Translator instance.
Use this to translate text.
"""


class Translation(commands.Cog, name='Translation', description='Commands used for localization and translation'):
    """
    Translation Cog.

    This cog contains commands helpful with translation and localization.
    """

    def __init__(self, bot: commands.Bot) -> None:
        """
        Initializes the cog.

        :param bot: The bot that this cog belongs to.
        :type bot: commands.Bot
        :return: Nothing.
        :rtype: None
        """
        self.bot: commands.Bot = bot

    @commands.hybrid_command(name="t", description="Translate a message")
    async def t(
            self,
            ctx: commands.Context,
            *,
            message: str = commands.parameter(
                description="The message you want to translate",
                displayed_name="Message",
            ),
    ) -> None:
        """
        Translates a given message to the user's preferred language.

        :param ctx: The context in which the command is invoked.
        :type ctx: commands.Context
        :param message: The message to translate
        :type message: str
        :return: None. The function only sends a Discord message, doesn't return anything in the code.
        :rtype: None
        """
        preferred_language_from_db: str = await ctx.bot.db.fetchval(
            'SELECT translate_to FROM users WHERE id = $1',
            ctx.author.id,
        )

        if preferred_language_from_db:
            destination_language: langcodes.Language = langcodes.get(preferred_language_from_db)
        else:
            destination_language: langcodes.Language = langcodes.get('en')

        translated: Translated = translator.translate(
            text=message.strip(),
            dest=destination_language.to_tag(),
            src='auto'
        )
        source_language: langcodes.Language = langcodes.get(translated.src)

        embed: discord.Embed = discord.Embed(
            color=discord.Color.teal(),
            description=translated.text,
            timestamp=ctx.message.created_at,
        )
        embed.set_footer(text=f'{source_language.display_name()} -> {destination_language.display_name()}')
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

        await ctx.reply(
            embed=embed,
            silent=True,
            ephemeral=True,
            allowed_mentions=discord.AllowedMentions.none(),
        )
        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.NotFound, discord.HTTPException) as e:
            print(f'Failed deleting message! {e}')

    @commands.hybrid_command(name="setlang", description="Set your preferred language for translation.")
    @ensure_user_is_in_database()
    async def setlang(
            self,
            ctx: commands.Context,
            language: Language = commands.parameter(
                description="The language you wish to translate to.",
                displayed_name="Language",
            ),
    ) -> None:
        old_language_from_db: str = await ctx.bot.db.fetchval(
            'SELECT translate_to FROM users WHERE id = $1',
            ctx.author.id,
        )
        if old_language_from_db:
            old_language: langcodes.Language = langcodes.get(old_language_from_db)
        else:
            old_language: langcodes.Language = langcodes.get('en')

        if old_language == language:
            embed: discord.Embed = discord.Embed(
                title="Language already set!",
                description=f'*{language.display_name()}* is already set.',
                color=discord.Color.teal(),
            )
            await ctx.reply(embed=embed, delete_after=60.0, ephemeral=True, silent=True)
            await ctx.message.delete(delay=60.0)
            return

        if language.to_tag() not in LANGUAGES:
            embed: discord.Embed = discord.Embed(
                title="Error!",
                description=f'__***{language.display_name()}***__** is a valid language, '
                            f'but it is not supported by '
                            f'**[__***Google Translator***__](https://translate.google.com/)**!**',
                color=discord.Color.red(),
            )
            await ctx.reply(embed=embed, delete_after=60.0, ephemeral=True, silent=True)
            await ctx.message.delete(delay=60.0)
            return

        await ctx.bot.db.execute(
            'UPDATE users SET translate_to = $2 WHERE id = $1',
            ctx.author.id,
            language.to_alpha3(),
        )

        embed: discord.Embed = discord.Embed(
            title="Language Preference Updated!",
            description=f'**{old_language.display_name()}** -> **{language.display_name()}**',
            color=discord.Color.green(),
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

        await ctx.reply(embed=embed, delete_after=60.0, ephemeral=True, silent=True)
        await ctx.message.delete()

    async def cog_command_error(self, ctx: commands.Context, error: Exception) -> None:
        await ctx.message.add_reaction('❌')
        await ctx.send_help(ctx.command)


@ensure_user_is_in_database_interaction()
async def translate_message_context_menu_callback(interaction: discord.Interaction, message: discord.Message):
    translate_to = await interaction.client.db.fetchval('SELECT translate_to FROM users WHERE id = $1', interaction.user.id)
    translate_to = langcodes.standardize_tag(translate_to)

    translated_text = translator.translate(text=message.content, dest=translate_to, src='auto')

    embed = discord.Embed(
        color=discord.Color.red(),
        title=f'{langcodes.get(translated_text.src).display_name()}'
              f' -> {langcodes.get(translated_text.dest).display_name()}',
        description=f'*{translated_text.text}*',
        timestamp=message.created_at,
    )
    embed.set_footer(text=message.author.display_name, icon_url=message.author.display_avatar.url)

    await interaction.response.send_message(embed=embed, ephemeral=True, silent=True, delete_after=60.0)


def setup(bot: commands.Bot):
    bot.add_cog(Translation(bot))

    translate_message_context_menu: app_commands.ContextMenu = app_commands.ContextMenu(
        name='Translate',
        callback=translate_message_context_menu_callback,
    )
    bot.tree.add_command(translate_message_context_menu)
