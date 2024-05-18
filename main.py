import discord
import asyncpg

from config import config
from bot import bot


# FUNCTIONS
async def setup_cogs():
    from cogs.Fun import Fun
    # from cogs.Moderation import Moderation
    from cogs.Games import Games
    from cogs.Info import Info
    from cogs.Translation import Translation
    
    await bot.add_cog(Fun(bot))
    # await bot.add_cog(Moderation(bot))
    await bot.add_cog(Games(bot))
    await bot.add_cog(Info(bot))
    await bot.add_cog(Translation(bot))
    await bot.tree.sync()

async def create_db_pool():
    bot.db = await asyncpg.create_pool(database='discord_engineer', user='postgres', password='1234')

@bot.event
async def on_ready():
    await setup_cogs()
    await create_db_pool()
    print(f"Logged in as {bot.user.name} ({bot.user.id})")

# LAUNCH
if __name__ == '__main__':
    bot.run(config['token'])