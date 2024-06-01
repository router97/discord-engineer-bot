import os
from dotenv import load_dotenv

from discord import Intents
from discord.ext.commands import Bot


load_dotenv()


intents = Intents.default()
intents.members = True
intents.message_content = True


bot = Bot(
    command_prefix=os.getenv('PREFIX'), 
    intents=intents, 
)