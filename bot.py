from discord import Intents
from discord.ext.commands import Bot
from googletrans import Translator

from config import config


intents = Intents.all()
bot = Bot(command_prefix = config['prefix'], intents = intents)
translator = Translator()