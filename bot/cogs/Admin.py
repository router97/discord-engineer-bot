import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
    
    @commands.is_owner()
    @commands.hybrid_command(name="reload", description="Reload an extension. OWNER-ONLY")
    async def reload(self, ctx: commands.Context, 
                     extension: str = commands.parameter(
                         displayed_name='Extension',
                         description='The extension name.\nEXAMPLE: `Admin` or `games`. case-insensitive.'
                         )
                     ) -> None:
        desired_extension = self.bot.extension_path + '.' + extension.title()
        if not desired_extension in self.bot.extensions:
            await ctx.reply(f'Extension {desired_extension} not present. Current Extensions: {self.bot.extensions}')
            return
        
        await asyncio.gather(
            self.bot.reload_extension(desired_extension),
            ctx.reply(f'Successfully reloaded {desired_extension}')
        )

    async def cog_command_error(self, ctx: commands.Context, error: Exception) -> None:
        await ctx.message.add_reaction('❌')
        await ctx.send_help(ctx.command)


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
