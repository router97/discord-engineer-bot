from os import getenv
from dotenv import load_dotenv

DISCORD_BOT_TOKEN = getenv('DISCORD_BOT_TOKEN')
COMMAND_PREFIX = getenv('COMMAND_PREFIX')

if not all(
        [DISCORD_BOT_TOKEN,
         COMMAND_PREFIX,
         ]):
    load_dotenv()

    DISCORD_BOT_TOKEN = getenv('DISCORD_BOT_TOKEN')
    COMMAND_PREFIX = getenv('COMMAND_PREFIX')
