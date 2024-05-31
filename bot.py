from discord import Intents
from discord.ext.commands import Bot
from googletrans import Translator

from config import config


intents = Intents.default()
intents.members = True
intents.message_content = True

bot = Bot(
    command_prefix=config['prefix'], 
    intents=intents, 
)
translator = Translator()