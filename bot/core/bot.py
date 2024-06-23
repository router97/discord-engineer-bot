"""
Bot Instance Creation Module
============================
This module creates a **bot instance** 
and stores it in it's **bot** variable.
"""

from typing import Optional
import importlib.metadata

from discord import Intents, Activity, ActivityType, Status, PartialEmoji
from discord.ext.commands import Bot

from .config import COMMAND_PREFIX


project_version: str = importlib.metadata.version('discord-engineer-bot')

# Configure bot intents
intents = Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True

# Create bot instance
bot = Bot(
    command_prefix=COMMAND_PREFIX,
    intents=intents,
)


async def setup_activity(name: Optional[str] = '.help') -> None:
    """
    Sets the bot's presence.

    :param name: The title of the activity.
    :type name: Optional[str]
    :return: The function changes the bot's presence, doesn't return anything in the code.
    :rtype: None
    """
    if len(name) > 128:
        name: str = name[:125] + "..."

    activity = Activity(
        name=name,
        type=ActivityType.playing,
        state=f'⚙️ v{project_version}',
        url='https://discord.com/oauth2/authorize?client_id=1167747112465858580',
    )
    await bot.change_presence(activity=activity, status=Status.online)
