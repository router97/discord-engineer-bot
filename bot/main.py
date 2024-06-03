"""
Discord Bot Launch Module
=========================
This module creates a **PostgreSQL** database connection, 
sets up the **cogs** and **commands** and runs the bot.
All variables are received from the **.env** file.
"""

import os
import logging
import atexit
import asyncio
import time
import datetime
from dotenv import load_dotenv

import asyncpg
from discord import Activity, ActivityType, PartialEmoji, Status

from core.bot import bot

from cogs.Fun import Fun
from cogs.Games import Games
from cogs.Info import Info
from cogs.Translation import Translation
from cogs.Utilities import Utilities


# Load environment variables from .env file
load_dotenv()

# Set up logging
logger = logging.getLogger(name = 'discord.log')


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
    Creates a **PostgreSQL** database connection pool using credentials from the **.env** file.
    
    If the connection fails, an error is logged.
    """
    try:
        bot.db = await asyncpg.create_pool(
            database=os.getenv('DATABASE_NAME'),
            user=os.getenv('DATABASE_USERNAME'),
            password=os.getenv('DATABASE_PASSWORD'),
            host=os.getenv('DATABASE_HOST', 'localhost'),
            port=int(os.getenv('DATABASE_PORT', '5432')),
        )
    except (asyncpg.PostgresError, OSError) as e:
        logger.error('DATABASE: Failed to connect to %s. Error: %s', os.getenv('DATABASE_NAME'), e)
    else:
        logger.info('DATABASE: Successfully connected to %s.', os.getenv('DATABASE_NAME'))


async def setup_activity() -> None:
    """
    Doc
    """
    activity: Activity = Activity(
        
    )
    await bot.change_presence(activity=activity, status=Status.online)


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
    bot.run(os.getenv('TOKEN'))


if __name__ == '__main__':
    atexit.register(lambda: asyncio.run(shutdown()))
    main()
