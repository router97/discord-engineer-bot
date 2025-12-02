import discord
from discord.ext import commands
from discord import app_commands

def predicate(ctx):
    return ctx.author.id == 982028805713588304

is_owner = commands.check(predicate)

class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
    
    
    @is_owner
    @commands.hybrid_command(name="reload", description="Reload an extension.")
    async def reload(self, ctx: commands.Context, extension) -> None:
        if not extension in self.bot.extensions:
            return
        
        desired_extension = self.bot.extension_path + '.' + extension
        await self.bot.reload_extension(desired_extension)

    async def cog_command_error(self, ctx: commands.Context, error: Exception) -> None:
        await ctx.message.add_reaction('❌')
        await ctx.send_help(ctx.command)


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
