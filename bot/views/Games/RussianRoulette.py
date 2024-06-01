"""
Russian Roulette
================

This module contains logic and message components for a game of russian roulette.
"""

from random import shuffle

import discord


class RussianRouletteView(discord.ui.View):
    """Russian Roulette"""
    
    BULLET_SYMBOL = '⦿'
    ICON_URL = 'https://miro.medium.com/v2/resize:fit:400/0*3bpWqAfhO_7Q3vHT.png'
    
    def __init__(self, user1: discord.Member, user2: discord.Member):
        super().__init__()
        self.user1 = user1
        self.user2 = user2
        self.player = user1
        self.barrel = [None, None, None, None, None, 'bullet']
        shuffle(self.barrel)
    
    async def setup_embed(self) -> discord.Embed:
        embed = discord.Embed(color=discord.Color.red())
        embed.set_author(name=f"{self.user1.display_name} vs {self.user2.display_name}")
        embed.add_field(name='Turn', value=self.user1.display_name)
        embed.add_field(name='Barrel', value=f"{self.BULLET_SYMBOL * len(self.barrel)}")
        embed.set_footer(text='Russian Roulette', icon_url=self.ICON_URL)
        return embed
    
    async def process_interaction(self, interaction: discord.interactions.Interaction, button: discord.ui.Button):
        """Process button interaction"""
        
        # Check if it's the user's move
        if interaction.user != self.player:
            return
        
        # Pull the trigger (remove and get the first element from the barrel)
        outcome = self.barrel.pop(0)

        # If there was a bullet, send a message and disable tbe button
        if outcome:
            await interaction.channel.send(f"{self.player.mention} застрелився тупен")
            self.button_pull_callback.disabled = True
        
        # Change the player
        self.player = self.user2 if self.player == self.user1 else self.user1
        
        # If the player is a bot, make a move and change the player back
        if self.player == interaction.client.user:
            if not self.barrel:
                outcome = None
            else:
                outcome = self.barrel.pop(0)
            if outcome:
                await interaction.channel.send(f"{self.player.mention} застрелився тупен")
                self.button_pull_callback.disabled = True
            self.player = self.user2 if self.player == self.user1 else self.user1
        
        # Fetch and edit the embed
        embed_new = interaction.message.embeds[0]
        embed_new.set_field_at(0, name='Turn', value=self.player.display_name)
        embed_new.set_field_at(1, name='Barrel', value=self.BULLET_SYMBOL*len(self.barrel) if self.barrel else 'Empty')
        
        # Accept the interaction
        await interaction.response.defer()
        
        # Edit the message
        await interaction.message.edit(embed=embed_new, view=self)
    
    @discord.ui.button(label='Pull', row=0, style=discord.ButtonStyle.primary)
    async def button_pull_callback(self, interaction: discord.interactions.Interaction, button: discord.ui.Button):
        await self.process_interaction(interaction, button)