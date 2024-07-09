"""
Bot Instance Creation Module
============================
This module creates a **bot instance** 
and stores it in it's **bot** variable.
"""

from typing import Optional

from discord import Intents, Activity, ActivityType, Status
from discord.ext import commands

import sys
import os

from .config import COMMAND_PREFIX
from .help_command import CustomHelpCommand

# Configure bot intents
intents = Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True

# Create bot instance
bot = commands.Bot(
    command_prefix=COMMAND_PREFIX,
    intents=intents,
    help_command=CustomHelpCommand(),
)


async def setup_activity(name: Optional[str] = '.help') -> None:
    """
    Sets the bot's presence.

    :param name: The title of the activity.
    :type name: Optional[str]
    :return: The function changes the bot's presence, doesn't return anything in the code.
    :rtype: None
    """
    from bot import __version__
    if len(name) > 128:
        name: str = name[:125] + "..."

    activity = Activity(
        name=name,
        type=ActivityType.playing,
        state=f'⚙️ v{__version__}',
        url='https://discord.com/oauth2/authorize?client_id=1167747112465858580',
    )
    await bot.change_presence(activity=activity, status=Status.online)
