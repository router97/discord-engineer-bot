from typing import Optional

from discord import Intents, Activity, ActivityType, Status
from discord.ext import commands
import logging

from .config import COMMAND_PREFIX
from .help_command import CustomHelpCommand


logger = logging.getLogger(name='discord.log')

bot = commands.Bot(
    command_prefix=COMMAND_PREFIX,
    intents=Intents.all(),
    help_command=CustomHelpCommand(),
)
bot.extension_path = 'cogs'


async def setup_activity(name: Optional[str] = f'{COMMAND_PREFIX}help') -> str:
    if len(name) > 128:
        name: str = name[:125] + "..."
    
    activity = Activity(
        name=name,
        type=ActivityType.playing,
    )
    await bot.change_presence(activity=activity, status=Status.online)
    logger.info("Bot presence changed. New presence: %s", name)
