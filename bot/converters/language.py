"""
This module contains converters related to languages.
"""
import discord
from discord.ext import commands

import langcodes


class Language(commands.Converter):
    """
    Converts an argument into a langcodes.Language object.
    """

    async def convert(self, ctx: commands.Context, argument: str) -> langcodes.Language:
        if langcodes.tag_is_valid(argument):
            language_by_code: langcodes.Language = langcodes.get(argument)
            if language_by_code.is_valid():
                return language_by_code

        normalized_name: str = argument.strip().casefold()
        language_by_name: langcodes.Language = langcodes.find(normalized_name)
        if language_by_name.is_valid():
            return language_by_name

        raise commands.BadArgument("Invalid language code or name")


LanguageConverter = Language  # Alias
