"""
Games
=====

This cog module contains some simple message-based games
using message components like embeds and buttons.
"""

import discord
from discord import app_commands
from discord.ext import commands
 
from views.Games.TicTacToe import TicTacToeView
from views.Games.RockPaperScissors import RockPaperScissorsView
from views.Games.RussianRoulette import RussianRouletteView


class Games(commands.Cog):
    """Some simple message-based games, using message components like: embeds, buttons."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.hybrid_command(name="ttt", description="A simple Tic-tac-toe game.")
    async def ttt(self, ctx: commands.Context,
        member: discord.Member = commands.parameter(
            converter=commands.MemberConverter,
            default=None,
            description="The user you want to play against.",
            displayed_default='Bot',
            displayed_name='Opponent', 
        )) -> None:
        
        # Default opponent to bot if none is provided
        if member is None:
            member = ctx.bot.user
        
        # Check if the user is trying to play with themselves
        if ctx.author == member:
            await ctx.reply(
                content="Yeah, I wonder who'd win.", 
                delete_after=60.0, 
                ephemeral=True, 
                silent=True, 
            )
            return
        
        # Set up message components
        view = TicTacToeView(user1=ctx.author, user2=member)
        embed = await view.setup_embed()
        
        # Send the message
        await ctx.reply(
            embed=embed, 
            silent=True, 
            view=view, 
        )
    
    @commands.hybrid_command(name="rps", description="A simple rock, paper, scissors game.")
    async def rps(self, ctx: commands.Context, 
        member: discord.Member = commands.parameter(
            converter=commands.MemberConverter, 
            default=None, 
            description="The user you want to play against.", 
            displayed_default='Bot', 
            displayed_name='Opponent', 
        )) -> None:
        
        # Default opponent to bot if none is provided
        if member is None:
            member = ctx.bot.user
        
        # Check if the user is trying to play with themselves
        if ctx.author == member:
            await ctx.reply(
                content="Yeah, I wonder who'd win.", 
                delete_after=60.0, 
                ephemeral=True, 
                silent=True, 
            )
            return
        
        # Set up message components
        view = RockPaperScissorsView(user1=ctx.author, user2=member)
        embed = await view.setup_embed()
        
        # Send the message
        await ctx.reply(
            embed=embed, 
            silent=True, 
            view=view, 
        )

    @commands.hybrid_command(name="rr", description="A simple russian roulette game.")
    async def rr(self, ctx: commands.Context, 
        member: discord.Member = commands.parameter(
            converter=commands.MemberConverter, 
            default=None, 
            description="The user you want to play against.", 
            displayed_default='Bot', 
            displayed_name='Opponent'
        )) -> None:

        # Default opponent to bot if none is provided
        if member is None:
            member = ctx.bot.user
        
        # Check if the user is trying to play with themselves
        if ctx.author == member:
            await ctx.reply(
                content="Yeah, I wonder who'd win.", 
                delete_after=60.0, 
                ephemeral=True, 
                silent=True, 
            )
            return
        
        # Set up message components
        view = RussianRouletteView(user1=ctx.author, user2=member)
        embed = await view.setup_embed()
        
        # Send the message
        await ctx.reply(
            embed=embed, 
            silent=True, 
            view=view, 
        )


async def ttt_context_menu_callback(interaction: discord.Interaction, member: discord.Member) -> None:
    """Rock, paper, scissors context menu."""
    
    # Check if the user is trying to play with themselves
    if interaction.user == member:
        await interaction.response.send_message(
            content="Yeah, I wonder who'd win.", 
            delete_after=60.0, 
            ephemeral=True, 
            silent=True, 
        )
        return

    # Set up message components
    view = TicTacToeView(user1=interaction.user, user2=member)
    embed = await view.setup_embed()
    
    # Send the message
    await interaction.response.send_message(
        embed=embed, 
        silent=True, 
        view=view, 
    )


async def rps_context_menu_callback(interaction: discord.Interaction, member: discord.Member) -> None:
    """Rock, paper, scissors context menu."""
    
    # Check if the user is trying to play with themselves
    if interaction.user == member:
        await interaction.response.send_message(
            content="Yeah, I wonder who'd win.", 
            delete_after=60.0, 
            ephemeral=True, 
            silent=True, 
        )
        return

    # Set up message components
    view = RockPaperScissorsView(user1=interaction.user, user2=member)
    embed = await view.setup_embed()
    
    # Send the message
    await interaction.response.send_message(
        embed=embed, 
        silent=True, 
        view=view, 
    )


async def rr_context_menu_callback(interaction: discord.Interaction, member: discord.Member) -> None:
    """Rock, paper, scissors context menu."""
    
    # Check if the user is trying to play with themselves
    if interaction.user == member:
        await interaction.response.send_message(
            content="Yeah, I wonder who'd win.", 
            delete_after=60.0, 
            ephemeral=True, 
            silent=True, 
        )
        return

    # Set up message components
    view = RussianRouletteView(user1=interaction.user, user2=member)
    embed = await view.setup_embed()
    
    # Send the message
    await interaction.response.send_message(
        embed=embed, 
        silent=True, 
        view=view, 
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
