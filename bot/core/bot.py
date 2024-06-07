"""
Bot Instance Creation Module
============================
This module creates a **bot instance** 
and stores it in it's **bot** variable.
"""

import os
from dotenv import load_dotenv

from discord import Intents
from discord.ext.commands import Bot

from core.config import COMMAND_PREFIX


# Configure bot intents
intents = Intents.default()
intents.members = True
intents.message_content = True

# Create bot instance
bot = Bot(
    command_prefix=COMMAND_PREFIX,
    intents=intents,
)
