import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import datetime

from views.Moderation.Mutes import MutesView


class InvalidDurationException(commands.CommandError):
    pass

class DurationConverter(commands.Converter):
    DURATION: dict[str, list[str]] = {
        'Year': ['y', 'year', 'years', 'г', 'год', 'года', 'лет'],
        'Months': ['mo', 'mos', 'month', 'months', 'мес', 'месяц', 'месяца', 'месяцев'],
        'Weeks': ['w', 'week', 'weeks', 'н', 'нед', 'неделя', 'недели', 'недель', 'неделю'],
        'Days':	['d', 'day', 'days', 'д', 'день', 'дня', 'дней'],
        'Hours': ['h', 'hour', 'hours', 'ч', 'час', 'часа', 'часов'],
        'Minutes': ['m', 'min', 'mins', 'minute', 'minutes', 'м', 'мин', 'минута', 'минуту', 'минуты', 'минут'],
        'Seconds': ['s', 'sec', 'secs', 'second', 'seconds', 'c', 'сек', 'секунда', 'секунду', 'секунды', 'секунд'],
    }
    DURATION_CONVERT_SECONDS: dict = {
        'Year': lambda x: x * 31556952,
        'Months': lambda x: x * 2629746,
        'Weeks': lambda x: x * 604800,
        'Days':	lambda x: x * 86400,
        'Hours': lambda x: x * 3600,
        'Minutes': lambda x: x * 60,
        'Seconds': lambda x: x,
    }

    async def convert(self, ctx: commands.Context, argument: str) -> datetime.timedelta:
        amount: int = 0
        timeframe = None
        
        if not argument[0].isdigit():
            raise InvalidDurationException("Doesn't start with a digit.")
        
        pointer = 0
        for i in argument:
            if not i.isdigit():
                break
            amount += int(i)
            pointer += 1
        else:
            raise InvalidDurationException("Only digits")
        
        for key, value in self.DURATION.items():
            if argument[pointer:] in value:
                timeframe = key
                break
        else:
            raise InvalidDurationException("No valid timeframe mentioned")
        
        return datetime.timedelta(
            seconds=self.DURATION_CONVERT_SECONDS[timeframe](amount)
        )





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
    

    commands.has_permissions(ban_members=True)
    @commands.hybrid_command(name="unban", description=".")
    async def unban(self, ctx: commands.Context, target: discord.User) -> None:
        try:
            await ctx.guild.unban(target)
        except Exception as e:
            await ctx.reply('An unknown error has occured.')
            raise e
        else:
            await ctx.reply(f'Successfully unbanned {target.id}', delete_after=15)


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
    

    commands.has_permissions(mute_members=True)
    @commands.hybrid_command(name="mute", description=".")
    async def mute(self, ctx: commands.Context, target: discord.Member, duration = commands.parameter(converter=DurationConverter(), default=datetime.timedelta(days=28)), reason: str = 'No reason provided') -> None:
        target_highest_role = target.roles[-1]
        user_highest_role = ctx.author.roles[-1]

        if user_highest_role <= target_highest_role:
            await ctx.reply('The person you are trying to mute has either a role higher than yours or the same.')
            return
        
        try:
            await target.timeout(duration, reason=reason)
        except Exception as e:
            await ctx.reply(f'An error has occured. {e}')
            # await target.timeout(None)
            raise e
        else:
            await ctx.reply(f'Successfully muted {target.display_name}({target.id}) for {duration.total_seconds()} seconds.', delete_after=15)

    commands.has_permissions(mute_members=True)
    @commands.hybrid_command(name="unmute", description=".")
    async def unmute(self, ctx: commands.Context, target: discord.Member) -> None:
        target_highest_role = target.roles[-1]
        user_highest_role = ctx.author.roles[-1]

        if user_highest_role <= target_highest_role:
            await ctx.reply('The person you are trying to mute has either a role higher than yours or the same.')
            return
        
        if not target.is_timed_out():
            await ctx.reply('They are not muted', delete_after=15)
            return

        try:
            await target.timeout(None)
        except Exception as e:
            await ctx.reply(f'An error has occured. {e}')
            raise e
        else:
            await ctx.reply(f'Successfully unmuted {target.display_name}({target.id})', delete_after=15)

    async def cog_command_error(self, ctx: commands.Context, error: Exception) -> None:
        try:
            await ctx.message.add_reaction('❌')
            result = await ctx.send_help(ctx.command)
            print(result)
        except Exception as e:
            print(e)


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
