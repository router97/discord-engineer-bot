import discord
from discord import app_commands
from discord.ext import commands

from views.Games.TicTacToe import TicTacToeView
from views.Games.RockPaperScissors import RockPaperScissorsView
from views.Games.RussianRoulette import RussianRouletteView
from views.Games.BuckshotRoulette import BuckshotRouletteLobbyView


class Games(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="ttt", description="A simple Tic-tac-toe game.", aliases=['tictactoe', 'tic-tac-toe'])
    async def ttt(self, ctx: commands.Context,
                  member: discord.Member = commands.parameter(
                      converter=commands.MemberConverter,
                      default=None,
                      description="The user you want to play against.",
                      displayed_default='Bot',
                      displayed_name='Opponent',
                  )) -> None:
        if member is None:
            member = ctx.bot.user

        if ctx.author == member:
            await ctx.reply(
                content="Yeah, I wonder who'd win.",
                delete_after=60.0,
                ephemeral=True,
                silent=True,
            )
            return

        view = TicTacToeView(user1=ctx.author, user2=member)
        embed = await view.setup_embed()

        await ctx.reply(
            embed=embed,
            silent=True,
            view=view,
        )

    @commands.hybrid_command(name="rps", description="A simple rock, paper, scissors game.", aliases=['rockpaperscissors'])
    async def rps(self, ctx: commands.Context,
                  member: discord.Member = commands.parameter(
                      converter=commands.MemberConverter,
                      default=None,
                      description="The user you want to play against.",
                      displayed_default='Bot',
                      displayed_name='Opponent',
                  )) -> None:
        if member is None:
            member = ctx.bot.user

        if ctx.author == member:
            await ctx.reply(
                content="Yeah, I wonder who'd win.",
                delete_after=60.0,
                ephemeral=True,
                silent=True,
            )
            return

        view = RockPaperScissorsView(user1=ctx.author, user2=member)
        embed = await view.setup_embed()

        await ctx.reply(
            embed=embed,
            silent=True,
            view=view,
        )

    @commands.hybrid_command(name="rr", description="Russian roulette", aliases=['russianroulette'])
    async def rr(self, ctx: commands.Context,
                 member: discord.Member = commands.parameter(
                     converter=commands.MemberConverter,
                     default=None,
                     description="The user you want to play against.",
                     displayed_default='Bot',
                     displayed_name='Opponent'
                 ),
                 extreme: str = 'no') -> None:
        if member is None:
            member = ctx.bot.user

        if ctx.author == member:
            await ctx.reply(
                content="???",
                delete_after=60.0,
                ephemeral=True,
                silent=True,
            )
            return
        extreme_converted = True if extreme=='extreme' else False
        view: RussianRouletteView = RussianRouletteView(ctx.author, member, extreme=extreme_converted)
        embed: discord.Embed = await view.setup_embed()

        await ctx.reply(
            embed=embed,
            view=view,
            allowed_mentions=discord.AllowedMentions(users=[ctx.author, member]),
        )
    
    @commands.hybrid_command(name="buckshot", description="Buckshot Roulette", aliases=['buckshotroulette'])
    async def buckshot(
        self,
        ctx: commands.Context,
        players: commands.Greedy[discord.Member] = commands.parameter(
            description='Players',
            displayed_name='Players',
        ),
        *,
        extreme: str = None
        ) -> None:
        extreme_converted = True if extreme=='extreme' else False
        players_including_author = list(players)
        players_including_author.append(ctx.author)

        players_cleaned_up = list(set(players_including_author))

        if len(players_cleaned_up) < 2:
            await ctx.reply(
                content="Need at least 2 players",
                delete_after=60.0,
                ephemeral=True,
                silent=True,
            )
            return
        
        message = await ctx.reply(
            embed=discord.Embed(title='Placeholder')
        )
        BuckshotRouletteLobbyView(message, players_cleaned_up, extreme_converted)


    # async def cog_command_error(self, ctx: commands.Context, error: Exception) -> None:
    #     await ctx.message.add_reaction('❌')
    #     await ctx.send_help(ctx.command)


async def ttt_context_menu_callback(interaction: discord.Interaction, member: discord.Member) -> None:
    if interaction.user == member:
        await interaction.response.send_message(
            content="Yeah, I wonder who'd win.",
            delete_after=60.0,
            ephemeral=True,
            silent=True,
        )
        return

    view = TicTacToeView(user1=interaction.user, user2=member)
    embed = await view.setup_embed()

    await interaction.response.send_message(
        embed=embed,
        silent=True,
        view=view,
    )


async def rps_context_menu_callback(interaction: discord.Interaction, member: discord.Member) -> None:
    if interaction.user == member:
        await interaction.response.send_message(
            content="Yeah, I wonder who'd win.",
            delete_after=60.0,
            ephemeral=True,
            silent=True,
        )
        return


    view = RockPaperScissorsView(user1=interaction.user, user2=member)
    embed = await view.setup_embed()

    await interaction.response.send_message(
        embed=embed,
        silent=True,
        view=view,
    )


async def rr_context_menu_callback(interaction: discord.Interaction, member: discord.Member) -> None:
    if interaction.user == member:
        await interaction.response.send_message(
            content="Yeah, I wonder who'd win.",
            delete_after=60.0,
            ephemeral=True,
            silent=True,
        )
        return

    view: RussianRouletteView = RussianRouletteView(user1=interaction.user, user2=member)
    embed: discord.Embed = await view.setup_embed()

    await interaction.response.send_message(
        embed=embed,
        view=view,
        allowed_mentions=discord.AllowedMentions(users=[interaction.user, member]),
    )


def setup(bot: commands.Bot):
    bot.add_cog(Games(bot))

    ttt_context_menu = app_commands.ContextMenu(
        name='Tic-Tac-Toe',
        callback=ttt_context_menu_callback,
    )
    bot.tree.add_command(ttt_context_menu)

    rps_context_menu = app_commands.ContextMenu(
        name='Rock, Paper, Scissors',
        callback=rps_context_menu_callback,
    )
    bot.tree.add_command(rps_context_menu)
    
    rr_context_menu = app_commands.ContextMenu(
        name='Russian Roulette',
        callback=rr_context_menu_callback,
    )
    bot.tree.add_command(rr_context_menu)
