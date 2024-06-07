from os import getenv
from dotenv import load_dotenv

DISCORD_BOT_TOKEN = getenv('DISCORD_BOT_TOKEN')
COMMAND_PREFIX = getenv('COMMAND_PREFIX')

DATABASE_NAME = getenv('DATABASE_NAME')
DATABASE_USER = getenv('DATABASE_USER')
DATABASE_PASSWORD = getenv('DATABASE_PASSWORD')
DATABASE_HOST = getenv('DATABASE_HOST', 'localhost')
DATABASE_PORT = getenv('DATABASE_PORT')

if not all(
        [DISCORD_BOT_TOKEN,
         COMMAND_PREFIX,
         DATABASE_NAME,
         DATABASE_USER,
         DATABASE_PASSWORD,
         DATABASE_HOST,
         DATABASE_PORT,
         ]):
    load_dotenv()

    DISCORD_BOT_TOKEN = getenv('DISCORD_BOT_TOKEN')
    COMMAND_PREFIX = getenv('COMMAND_PREFIX')

    DATABASE_NAME = getenv('DATABASE_NAME')
    DATABASE_USER = getenv('DATABASE_USER')
    DATABASE_PASSWORD = getenv('DATABASE_PASSWORD')
    DATABASE_HOST = getenv('DATABASE_HOST', 'localhost')
    DATABASE_PORT = getenv('DATABASE_PORT')
