import discord
from discord.ext import commands
from discord import app_commands

def ensure_user_is_in_database():
    async def predicate(ctx):
        user = await ctx.bot.db.fetchrow('SELECT 1 FROM users WHERE user_id = $1', ctx.author.id)
        if not user:
            await ctx.bot.db.execute('INSERT INTO users (user_id) VALUES ($1)', ctx.author.id)
        return True

    return commands.check(predicate)

def ensure_user_is_in_database_interaction():
    async def predicate(interaction: discord.Interaction):
        bot = interaction.client
        user = await bot.db.fetchrow('SELECT 1 FROM users WHERE user_id = $1', interaction.user.id)
        if not user:
            await bot.db.execute('INSERT INTO users (user_id) VALUES ($1)', interaction.user.id)
        return True

    return app_commands.check(predicate)