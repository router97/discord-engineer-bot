import datetime
import time
from random import choice

import discord
from discord.ext import commands
from discord import app_commands
from faker import Faker

from  core.bot import setup_activity
from . import acceptable_errors

from core.bot import logger

faker = Faker()


class Fun(commands.Cog):
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
        await ctx.reply(faker.ipv4())

    @commands.hybrid_command(name="fog", description="The fog is coming...")
    async def fog(self, ctx: commands.Context) -> None:
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
        await ctx.reply(choice(self.RANDOM_REPLIES))

    @commands.hybrid_command(name='do', description='Change the presence of the bot.')
    async def do(
            self,
            ctx: commands.Context,
            *,
            name: str = commands.parameter(
                description="The new activity. Up to 128 characters long.",
                displayed_name='Activity',
            )
    ) -> None:
        if not name:
            raise commands.MissingRequiredArgument()

        await setup_activity(name)
        
        await ctx.reply(
            content=f"Changed the bot's presence to `{name}`.",
            allowed_mentions=discord.AllowedMentions.none(),
            ephemeral=True,
            silent=True,
            delete_after=30,
        )
        await ctx.message.delete()

    async def cog_command_error(self, ctx: commands.Context, error: Exception) -> None:
        await ctx.message.add_reaction('❌')
        await ctx.send_help(ctx.command)

        if type(error) not in acceptable_errors:
            logger.error("Error in cog %s.", self.qualified_name, exc_info=error)


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
