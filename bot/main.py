import logging
import atexit
import asyncio

from core.bot import bot, setup_activity
import core.config as config

logger = logging.getLogger(name='discord.log')

extensions = ['Games', 'Info', 'Utilities', 'Fun']
extension_path = 'cogs'

async def setup_cogs() -> None:
    for extension in extensions:
        await bot.load_extension(f"{extension_path}.{extension}")
    
    await bot.tree.sync()


@bot.event
async def on_ready() -> None:
    await setup_cogs()
    await setup_activity()
    logger.info("Logged in as %s (User ID: %s).", bot.user.display_name, bot.user.id)


async def shutdown() -> None:
    logger.info("Bot is shutting down.")


@bot.command()
async def reload(ctx, extension):
    if not extension in extensions:
        return
    
    desired_extension = extension_path + '.' + extension
    await bot.reload_extension(desired_extension)


@bot.event
async def on_disconnect() -> None:
    await shutdown()


def main() -> None:
    bot.run(config.DISCORD_BOT_TOKEN)


if __name__ == '__main__':
    atexit.register(lambda: asyncio.run(shutdown()))
    main()
