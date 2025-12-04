import atexit
import asyncio

from core.bot import bot, setup_activity, logger
import core.config as config

from cogs import extensions


async def setup_cogs() -> None:
    for extension in extensions:
        await bot.load_extension(f"{bot.extension_path}.{extension}")
        logger.info('Loaded extension %s.', f"{bot.extension_path}.{extension}")
    
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
    bot.run(config.DISCORD_BOT_TOKEN)


if __name__ == '__main__':
    atexit.register(lambda: asyncio.run(shutdown()))
    main()
