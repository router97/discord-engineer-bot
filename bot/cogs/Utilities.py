import datetime
from random import randint, choice

import discord
from discord.ext import commands


class Utilities(commands.Cog, name='Utilities', description='Somewhat useful commands'):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @commands.hybrid_command(name="rand", description="Generate a random number")
    async def rand(
            self,
            ctx: commands.Context,
            fro: int = commands.parameter(
                default=0,
                description='From which number',
                displayed_default='0',
                displayed_name='From',
            ),
            to: int = commands.parameter(
                default=100,
                description='To which number',
                displayed_default='100',
                displayed_name='To',
            ),
    ) -> None:
        if fro == to or fro > to:
            embed = discord.Embed(
                title="Error!",
                description=f'**Invalid range(from {fro} to {to})!**',
                color=discord.Color.red(),
            )
            await ctx.message.add_reaction('❌')
        else:
            random_number: int = randint(fro, to)

            embed: discord.Embed = discord.Embed(
                title=str(random_number),
                color=discord.Color.teal()
            )
            embed.set_author(name=f'A random number between {fro} and {to}:')

        await ctx.reply(
            embed=embed,
            silent=True,
            ephemeral=True,
            delete_after=60.0,
            allowed_mentions=discord.AllowedMentions.none(),
        )
        try:
            await ctx.message.delete(delay=60.0)
        except (discord.Forbidden, discord.NotFound, discord.HTTPException) as e:
            print(f'Failed deleting message! {e}')

    @commands.hybrid_command(name="randmember", description="Ping a random member from the server")
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def randmember(
            self,
            ctx: commands.Context
    ) -> None:
        real_members: list[discord.Member] = [member for member in ctx.guild.members if not member.bot]

        if not real_members:
            embed = discord.Embed(
                title="Error!",
                description=f'**There are no real members on this server!**',
                color=discord.Color.red(),
            )
            await ctx.message.add_reaction('❌')
            await ctx.reply(
                embed=embed,
                silent=True,
                ephemeral=True,
                delete_after=60.0,
                allowed_mentions=discord.AllowedMentions.none(),
            )
            try:
                await ctx.message.delete(delay=60.0)
            except (discord.Forbidden, discord.NotFound, discord.HTTPException) as e:
                print(f'Failed deleting message! {e}')

        random_member: discord.Member = choice(real_members)
        await ctx.reply(random_member.mention)

    @commands.hybrid_command(name="listroles", description="Produce an embed, listing specified roles and their members")
    @commands.guild_only()
    async def listroles(
            self,
            ctx: commands.Context,
            roles: commands.Greedy[discord.Role] = commands.parameter(
                description='The roles to list',
                displayed_name='Roles',
            ),
            *,
            title: str = commands.parameter(
                description='The title of the produced embed',
                displayed_name='Title',
            ),
    ) -> None:
        embed: discord.Embed = discord.Embed(
            color=discord.Color.teal(),
            title=title,
            timestamp=datetime.datetime.now(),
        )
        embed.set_thumbnail(url=ctx.guild.icon.url)

        for role in roles:
            embed.add_field(
                name=role.name,
                value='\n'.join(f'- {member.mention}' for member in role.members) if role.members else '-',
                inline=False
            )

        await ctx.reply(
            embed=embed,
            silent=True,
            ephemeral=True,
            delete_after=60.0,
            allowed_mentions=discord.AllowedMentions.none(),
        )
        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.NotFound, discord.HTTPException):
            pass

    async def cog_command_error(self, ctx: commands.Context, error: Exception) -> None:
        await ctx.message.add_reaction('❌')
        await ctx.send_help(ctx.command)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utilities(bot))
