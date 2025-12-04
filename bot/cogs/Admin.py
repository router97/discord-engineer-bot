import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from database.models.guilds import GuildMemberConfig

from core.bot import logger
from . import acceptable_errors

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
            await ctx.reply(f'Extension `{desired_extension}` not present.', delete_after=15)
            return
        
        await asyncio.gather(
            self.bot.reload_extension(desired_extension),
            ctx.reply(f'Successfully reloaded {desired_extension}', delete_after=15)
        )
        logger.info('Reloaded extension %s.', desired_extension)

    @commands.hybrid_command(name="get", description="test")
    async def get(self, ctx: commands.Context) -> None:
        result = GuildMemberConfig.get(
            guild_id = ctx.guild.id,
            _id = ctx.author.id
        )
        await ctx.reply(str(result))
    
    @commands.hybrid_command(name="save", description="test")
    async def save(self, ctx: commands.Context) -> None:
        newconfig = GuildMemberConfig(
            guild_id=ctx.guild.id,
            id=ctx.author.id,
        )
        newconfig.save()
        await ctx.reply('Saved', delete_after=15)
        

    async def cog_command_error(self, ctx: commands.Context, error: Exception) -> None:
        await ctx.message.add_reaction('❌')
        await ctx.send_help(ctx.command)

        if type(error) not in acceptable_errors:
            logger.error("Error in cog %s.", self.qualified_name, exc_info=error)


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
