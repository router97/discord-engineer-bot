import logging
from typing import Optional

import aiohttp

from discord import Intents, Activity, ActivityType, Status
from discord.ext import commands

from cogs import extensions
from . import config
from .help_command import CustomHelpCommand


__all__ = [
    'logger',
    'bot',
]


class EngineerBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extension_path: str = 'cogs'
        self._api_enabled = False
        self.session: aiohttp.ClientSession = ...
    
    async def on_ready(self) -> None:
        if config.API_URL:
            bot.session = aiohttp.ClientSession(base_url=config.API_URL)
            self._api_enabled = True
        
        await self.setup_cogs()
        await self.setup_activity()
        logger.info("Logged in as %s (User ID: %s).", bot.user.display_name, bot.user.id)
    
    async def setup_cogs(self) -> None:
        for extension in extensions:
            try:
                await bot.load_extension(f"{bot.extension_path}.{extension}")
                logger.info('Loaded extension %s.', f"{bot.extension_path}.{extension}")
            except commands.ExtensionError as e:
                logger.error('Failed to load extension %s.', f"{bot.extension_path}.{extension}", exc_info=True)
        
        await bot.tree.sync()
    
    async def on_disconnect() -> None:
        logger.info("Bot is shutting down.")
    
    async def setup_activity(self, name: Optional[str] = f'{config.COMMAND_PREFIX}help') -> str:
        if len(name) > 128:
            name: str = name[:125] + "..."
        
        activity = Activity(
            name=name,
            type=ActivityType.playing,
        )
        await self.change_presence(activity=activity, status=Status.online)
        logger.info("Bot presence changed. New presence: %s", name)


logger = logging.getLogger(name='discord.log')

bot: EngineerBot = EngineerBot(
    command_prefix=config.COMMAND_PREFIX,
    intents=Intents.all(),
    help_command=CustomHelpCommand(),
)
