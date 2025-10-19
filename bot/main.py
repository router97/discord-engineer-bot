import logging
import atexit
import asyncio

from core.bot import bot, setup_activity
from core.config import *

from cogs.Fun import Fun
from cogs.Games import Games
from cogs.Info import Info
from cogs.Utilities import Utilities


logger = logging.getLogger(name='discord.log')


async def setup_cogs() -> None:
    await bot.add_cog(Fun(bot))
    await bot.add_cog(Games(bot))
    await bot.add_cog(Info(bot))
    await bot.add_cog(Utilities(bot))
    await bot.tree.sync()


@bot.event
async def on_ready() -> None:
    await setup_cogs()
    await setup_activity()
    logger.info("Logged in as %s (User ID: %s).", bot.user.display_name, bot.user.id)


async def shutdown() -> None:
    logger.info("Bot is shutting down.")


@bot.event
async def on_disconnect() -> None:
    await shutdown()


def main() -> None:
    bot.run(DISCORD_BOT_TOKEN)


if __name__ == '__main__':
    atexit.register(lambda: asyncio.run(shutdown()))
    main()
