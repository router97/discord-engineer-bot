from os import getenv
from dotenv import load_dotenv


__all__ = [
    'DISCORD_BOT_TOKEN',
    'COMMAND_PREFIX',
    'API_URL',
]


DISCORD_BOT_TOKEN = getenv('DISCORD_BOT_TOKEN')
COMMAND_PREFIX = getenv('COMMAND_PREFIX')
API_URL = getenv('API_URL')


if not all((DISCORD_BOT_TOKEN, COMMAND_PREFIX, API_URL)):
    load_dotenv()

    DISCORD_BOT_TOKEN = getenv('DISCORD_BOT_TOKEN')
    COMMAND_PREFIX = getenv('COMMAND_PREFIX')
    API_URL = getenv('API_URL')
