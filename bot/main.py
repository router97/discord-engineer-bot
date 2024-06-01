import os
import logging
from dotenv import load_dotenv

import asyncpg

from core.bot import bot

from cogs.Fun import Fun
from cogs.Games import Games
from cogs.Info import Info
from cogs.Translation import Translation
from cogs.Utilities import Utilities


load_dotenv()
logger = logging.getLogger(name='discord.log')


async def setup_cogs() -> None:
    await bot.add_cog(Fun(bot))
    await bot.add_cog(Games(bot))
    await bot.add_cog(Info(bot))
    await bot.add_cog(Translation(bot))
    await bot.add_cog(Utilities(bot))
    await bot.tree.sync()


async def create_db_pool() -> None:
    try:
        bot.db = await asyncpg.create_pool(
            database=os.getenv('DATABASE_NAME'),
            user=os.getenv('DATABASE_USERNAME'),
            password=os.getenv('DATABASE_PASSWORD')
        )
    except asyncpg.ConnectionDoesNotExistError:
        logger.error(f"Failed to create database pool.")


@bot.event
async def on_ready() -> None:
    await create_db_pool()
    await setup_cogs()
    logger.info(f"Logged in as {bot.user.display_name} (User ID: {bot.user.id}).")


if __name__ == '__main__':
    bot.run(os.getenv('TOKEN'))
