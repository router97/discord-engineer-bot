from discord.ext import commands

__all__ = 'extensions'

extensions = [
    'Games', 
    'Info', 
    'Utilities', 
    'Fun', 
    'Admin', 
    'Moderation',
    'Ranking',
]

acceptable_errors = [
    commands.MissingRequiredArgument,
    commands.CommandNotFound,
]