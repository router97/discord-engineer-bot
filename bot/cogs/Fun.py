"""
Fun
===

This cog module contains miscellaneous, non-essential commands.
"""

import datetime
import time
from random import choice

import discord
from discord.ext import commands
from faker import Faker

from core.bot import setup_activity

faker = Faker()


class Fun(commands.Cog):
    """
    Miscellaneous commands.

    This class contains non-essential random commands.
    """
    RANDOM_REPLIES: list[str] = [
        "I'm good",
        "KYS = Keep Yourself Safe",
        "Nah",
        "I'll pass on that one",
        "No, thanks",
        "/me Лицом к стене! 1... 2... 3... Стреляю!",
    ]
    FOG_ARRIVAL_TIMESTAMP: float = datetime.datetime(2026, 4, 7).timestamp()

    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @commands.hybrid_command(name="ip", description="Generate a random IPv4 address.")
    async def ip(self, ctx: commands.Context) -> None:
        """
        Replies with a random **IPv4** address generated using **Faker**.

        :param ctx: The context in which the command is invoked.
        :type ctx: commands.Context
        :return: None. The function only sends a Discord message, doesn't return anything in the code.
        :rtype: None
        """
        await ctx.reply(faker.ipv4())

    @commands.hybrid_command(name="fog", description="The fog is coming...")
    async def fog(self, ctx: commands.Context) -> None:
        """
        Replies with how much time is left until the **fog** comes.

        :param ctx: The context in which the command is invoked.
        :type ctx: commands.Context
        :return: The function only sends a Discord message, doesn't return anything in the code.
        :rtype: None
        """
        current_time: float = time.time()
        time_difference: float = self.FOG_ARRIVAL_TIMESTAMP - current_time

        if time_difference <= 0:
            await ctx.reply('The fog is here...')

        days, remainder = divmod(time_difference, 24 * 3600)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        remaining_time_string: str = (f'{days:.0f} days, '
                                      f'{hours:.0f} hours, '
                                      f'{minutes:.0f} minutes, '
                                      f'{seconds:.0f} seconds '
                                      f'remaining...')
        await ctx.reply(remaining_time_string)

    @commands.hybrid_command(name="kys", description="Kys.")
    async def kys(self, ctx: commands.Context) -> None:
        """
        Replies with a random string from ``self.RANDOM_REPLIES``.

        :param ctx: The context in which the command is invoked.
        :type ctx: commands.Context
        :return: The function only sends a Discord message, doesn't return anything in the code.
        :rtype: None
        """
        await ctx.reply(choice(self.RANDOM_REPLIES))

    @commands.command(name='do', description='Change the presence of the bot.')
    async def do(
            self,
            ctx: commands.Context,
            *,
            name: str = commands.parameter(
                description="The text, which would be set as the bot's activity.",
                displayed_name='Name',
            )
    ) -> None:
        """
        Changes the bot's presence.

        :param ctx: The context in which the command is invoked.
        :type ctx: commands.Context
        :param name: The text, which would be set as the bot's activity.
        :type name: str
        :return: The function only sends a Discord message, doesn't return anything in the code.
        :rtype: None
        """
        await setup_activity(name)
        await ctx.reply(
            content=f"Changed the bot's presence to `{name}`.",
            delete_after=60.0,
            allowed_mentions=discord.AllowedMentions.none(),
            ephemeral=True,
            silent=True,
        )

    async def cog_command_error(self, ctx: commands.Context, error: Exception) -> None:
        await ctx.send_help(ctx.command)


def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))
