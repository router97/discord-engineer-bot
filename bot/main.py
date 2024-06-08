"""
Discord Bot Launch Module
=========================
This module creates a **Postgres** database connection,
sets up the **cogs** and **commands** and runs the bot.
Uses environment variables, if none, defaults to .env file.
"""

import logging
import atexit
import asyncio

import asyncpg

from core.bot import bot, setup_activity
from core.config import *

from cogs.Fun import Fun
from cogs.Games import Games
from cogs.Info import Info
from cogs.Translation import Translation
from cogs.Utilities import Utilities

# Set up logging
logger = logging.getLogger(name='discord.log')


async def setup_cogs() -> None:
    """Adds **cogs** and **commands** to the bot and synchronizes the command tree."""
    await bot.add_cog(Fun(bot))
    await bot.add_cog(Games(bot))
    await bot.add_cog(Info(bot))
    await bot.add_cog(Translation(bot))
    await bot.add_cog(Utilities(bot))
    await bot.tree.sync()


async def create_db_pool() -> None:
    """
    Creates a **Postgres** database connection pool using credentials from the **.env** file.
    
    If the connection fails, an error is logged.
    """
    try:
        bot.db = await asyncpg.create_pool(
            database=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_HOST,
            port=int(DATABASE_PORT),
        )
    except (asyncpg.PostgresError, OSError) as e:
        logger.error('DATABASE: Failed to connect to %s. Error: %s', DATABASE_NAME, e)
    else:
        logger.info('DATABASE: Successfully connected to %s.', DATABASE_NAME)


@bot.event
async def on_ready() -> None:
    """
    Event handler that is called when the bot is ready.
    
    This function sets up the database connection pool and registers the bot's cogs.
    """
    await create_db_pool()
    await setup_cogs()
    await setup_activity()
    logger.info("Logged in as %s (User ID: %s).", bot.user.display_name, bot.user.id)


async def shutdown() -> None:
    """Shuts down the bot, closing the database pool."""
    if hasattr(bot, 'db'):
        await bot.db.close()
    logger.info("Bot is shutting down.")


@bot.event
async def on_disconnect() -> None:
    """Event handler that is called when the bot disconnects."""
    await shutdown()


def main() -> None:
    """
    The main entry point of the script.
    
    This function starts the bot using the token from the **.env** file.
    """
    bot.run(DISCORD_BOT_TOKEN)


if __name__ == '__main__':
    atexit.register(lambda: asyncio.run(shutdown()))
    main()
