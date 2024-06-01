import discord
from discord.ext import commands
from discord import app_commands


def ensure_user_is_in_database():
    async def predicate(ctx: commands.Context):
        bot = ctx.bot
        
        if not hasattr(bot, 'db'):
            raise RuntimeError("Bot has no database connection attribute 'db'")
        
        user = await bot.db.fetchrow('SELECT 1 FROM users WHERE id = $1', ctx.author.id)
        
        if not user:
            await bot.db.execute('INSERT INTO users (id) VALUES ($1)', ctx.author.id)
        return True

    return commands.check(predicate)


def ensure_user_is_in_database_interaction():
    async def predicate(interaction: discord.Interaction):
        bot = interaction.client
        
        if not hasattr(bot, 'db'):
            raise RuntimeError("Bot has no database connection attribute 'db'")
        
        user = await bot.db.fetchrow('SELECT 1 FROM users WHERE id = $1', interaction.user.id)
        if not user:
            await bot.db.execute('INSERT INTO users (id) VALUES ($1)', interaction.user.id)
        return True

    return app_commands.check(predicate)
