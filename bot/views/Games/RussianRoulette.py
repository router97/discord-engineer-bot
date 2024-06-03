"""
Russian Roulette
================

This module contains logic and message components for a game of russian roulette.
"""

import time
import datetime
from enum import Enum
from random import randint

import discord


class Round(Enum):
    """
    Enum representing a round in a revolver.
    Can be either live or empty.
    """
    EMPTY = 0
    LIVE = 1


class Revolver:
    """
    A class representing a revolver.
    """
    def __init__(self, size: int = 6, live_rounds: int = 1) -> None:
        """
        Initiate a revolver and initiate it's chamber.
        """
        if live_rounds > size:
            raise ValueError("The number of live rounds cannot be more than the chamber can hold!")
        
        if live_rounds < 0:
            raise ValueError("The number of live rounds cannot be negative!")
        
        if live_rounds == 0:
            raise ValueError("What's the point of the game if you don't load anything?")
        
        if size < 2:
            raise ValueError("The chamber size must be more than 1.")
        
        self.size = size
        self.__chamber = [Round.LIVE for _ in range(live_rounds)]
        self.__chamber.extend([Round.EMPTY for _ in range(size - live_rounds)])
        self.current_position = 0

    
    def fire(self) -> Round:
        """
        Fires a round, imitating a real revolver trigger pull.
        In code, returns the current round and makes it empty in the chamber.
        """
        fired_round = self.__chamber[self.current_position]
        self.__chamber[self.current_position] = Round.EMPTY
        return fired_round
    
    
    def spin(self) -> None:
        """
        Spins the revolver's chamber, imitating a real chamber spin.
        """
        self.current_position = randint(0, self.size - 1)


class RussianRouletteView(discord.ui.View):
    """
    A Russian Roulette view.
    """
    FIRE_EMOJI: str = '🔥'
    
    
    def __init__(self, user1: discord.Member, user2: discord.Member) -> None:
        """
        Initiates the view, takes two players as arguments.
        First user makes the first move.
        """
        super().__init__()
        self.user1 = user1
        self.user2 = user2
        self.player = user1
        self.revolver = Revolver()
    
    
    async def setup_embed(self, embed_to_update: discord.Embed = None) -> discord.Embed:
        """
        Sets up or updates the embed for the game.
        """
        if embed_to_update is None:
            embed: discord.Embed = discord.Embed(
                color=discord.Color.red(),
                title='Russian Roulette',
                description=f'A game of russian roulette between {self.user1.mention} and {self.user2.mention}.',
                timestamp=datetime.datetime.now(),
            )
            embed.add_field(name='Shooter', value=self.player.mention)
            return embed
        
        embed_to_update.set_field_at(0, name='Shooter', value=self.player.mention)
        return embed_to_update
            
    
    @discord.ui.button(
        label='Fire',
        custom_id='button_fire',
        style=discord.ButtonStyle.red,
        emoji=FIRE_EMOJI,
        row=0,
    )
    async def button_fire_callback(self, interaction: discord.Interaction, button: discord.Button) -> None:
        """
        Processes the interaction when a player pulls the trigger.
        """
        # Check if it's the user's move
        if interaction.user.id != self.player.id:
            return
        
        # Accept interaction if so
        await interaction.response.defer()
        
        # Spin the chamber
        self.revolver.spin()
        
        # Fetch the message's current embed
        current_embed: discord.Embed = interaction.message.embeds[0]
        
        # Fire the revolver
        round_shot: Round = self.revolver.fire()
        
        if round_shot == Round.LIVE:
            current_embed.set_footer(text=f"{self.player.display_name} Lost!")
            for child in self.children:
                child.disabled = True
            await interaction.message.edit(embed=current_embed, view=self)
            return
        
        elif round_shot == Round.EMPTY:
            
            # Pass the revolver to the other player
            self.player: discord.Member = self.user2 if self.player == self.user1 else self.user1
            
            new_embed: discord.Embed = await self.setup_embed(current_embed)
            await interaction.message.edit(embed=new_embed, view=self)
        
        # If the player is a bot, make a move and change the player back
        if self.player == interaction.client.user:
            time.sleep(2)
            self.revolver.spin()
            # Fetch the message's current embed
            current_embed: discord.Embed = interaction.message.embeds[0]
            
            # Fire the revolver
            round_shot: Round = self.revolver.fire()
            
            if round_shot == Round.LIVE:
                current_embed.set_footer(text=f"{self.player.display_name} Lost!")
                for child in self.children:
                    child.disabled = True
                await interaction.message.edit(embed=current_embed, view=self)
            
            elif round_shot == Round.EMPTY:
                
                # Pass the revolver to the other player
                self.player: discord.Member = self.user2 if self.player == self.user1 else self.user1
                
                new_embed: discord.Embed = await self.setup_embed(current_embed)
                await interaction.message.edit(embed=new_embed, view=self)
