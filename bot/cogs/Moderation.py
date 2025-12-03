import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from views.Moderation.Mutes import MutesView


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
    
    commands.has_permissions(ban_members=True)
    @commands.hybrid_command(name="ban", description=".")
    async def ban(self, ctx: commands.Context, target: discord.Member, reason: str = 'No reason provided') -> None:
        target_highest_role = target.roles[-1]
        user_highest_role = ctx.author.roles[-1]

        if user_highest_role <= target_highest_role:
            await ctx.reply('The person you are trying to ban has either a role higher than yours or the same.')
            raise Exception()
        
        try:
            await target.ban(reason=reason)
        except Exception as e:
            await ctx.reply('An unknown error has occured.')
            raise e
        else:
            ctx.reply(f'Successfully banned {target.display_name}({target.id})', delete_after=15)
    
    commands.has_permissions(kick_members=True)
    @commands.hybrid_command(name="kick", description=".")
    async def kick(self, ctx: commands.Context, 
                   target: discord.Member, 
                   reason: str = commands.parameter(
                       default='No reason provided',
                   )
                   ) -> None:
        target_highest_role = target.roles[-1]
        user_highest_role = ctx.author.roles[-1]

        if user_highest_role <= target_highest_role:
            await ctx.reply('The person you are trying to kick has either a role higher than yours or the same.')
            return
        
        
        try:
            await target.kick(reason=reason)
        except Exception as e:
            await ctx.reply('An unknown error has occured.')
            raise e
        else:
            await ctx.reply(f'Successfully kicked {target.display_name}({target.id})', delete_after=15)


    commands.has_permissions(mute_members=True)
    @commands.hybrid_command(name="mutes", description=".")
    async def mutes(self, ctx: commands.Context) -> None:
        mutes_info = [
            {'member': member, 'until': member.timed_out_until} for member in ctx.guild.members if member.is_timed_out()
        ]

        if not mutes_info:
            await ctx.reply('No one is currently muted in this guild.')
            return

        message = await ctx.reply('.')
        view = MutesView(data = mutes_info, message = message)
                   


    # async def cog_command_error(self, ctx: commands.Context, error: Exception) -> None:
    #     try:
    #         await ctx.message.add_reaction('❌')
    #         result = await ctx.send_help(ctx.command)
    #         print(result)
    #     except Exception as e:
    #         print(e)


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
