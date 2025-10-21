import time
import datetime
from enum import Enum
from random import randint, shuffle
from asyncio import sleep

import discord


class Round(Enum):
    EMPTY = 0
    LIVE = 1


class Revolver:
    def __init__(self, size: int = 6, live_rounds: int = 1) -> None:
        if live_rounds > size:
            raise ValueError("The number of live rounds cannot be more than the cylinder can hold")
        
        if live_rounds < 0:
            raise ValueError("The number of live rounds cannot be negative")
        
        if live_rounds == 0:
            raise ValueError("zero lives?")
        
        if size < 2:
            raise ValueError("thats too small of a cylinder you got there")
        
        self.size = size
        self.__cylinder = [Round.LIVE for _ in range(live_rounds)]
        self.__cylinder.extend([Round.EMPTY for _ in range(size - live_rounds)])
        shuffle(self.__cylinder)
        self.current_position = 0

    
    def fire(self) -> Round:
        fired_round = self.__cylinder[self.current_position]
        self.__cylinder[self.current_position] = Round.EMPTY
        
        if self.current_position + 1 < self.size:
            self.current_position += 1
        elif self.current_position + 1 == self.size:
            self.current_position = 0
        
        return fired_round
    
    
    def spin(self) -> None:
        self.current_position = randint(0, self.size - 1)

    def give_cylinder(self) -> str:
        return str(self.__cylinder) + f'cursor: {self.current_position}'
    
    def return_cylinder(self) -> list:
        return self.__cylinder.copy()


class RussianRouletteView(discord.ui.View):
    EMPTY_SYMBOL = '◯'
    SPENT_SYMBOL = '⦸'

    def __init__(self, user1: discord.Member, user2: discord.Member, extreme: bool = False) -> None:
        super().__init__()
        self.player1: discord.Member = user1
        self.player2: discord.Member = user2
        self.player_active: discord.Member = user1
        
        self.can_end_round = False

        self.history = []

        self.revolver: Revolver = Revolver()
        self.extreme = extreme
    
    
    async def setup_embed(self, embed_to_update: discord.Embed = None) -> discord.Embed:
        if embed_to_update is None:
            embed: discord.Embed = discord.Embed(
                color=discord.Color.red() if not self.extreme else discord.Color.dark_gray(),
                title='Russian Roulette' if not self.extreme else 'RUSSIAN ROULETTE (EXTREME)',
                description=f'{self.player1.mention} and {self.player2.mention}.',
                timestamp=datetime.datetime.now(),
            )
            embed.add_field(name='Holding the gun:', value=self.player_active.mention)
            embed.add_field(name='Actions taken:', value=' | '.join(self.history))
            return embed
        
        embed_to_update.set_field_at(1, name='Actions taken:', value=' | '.join(self.history))
        embed_to_update.set_field_at(0, name='Holding the gun:', value=self.player_active.mention)
        return embed_to_update
            
    
    @discord.ui.button(
        label='Pull the trigger',
        custom_id='button_pull',
        style=discord.ButtonStyle.red,
        row=0,
    )
    async def button_fire_callback(self, interaction: discord.Interaction, button: discord.Button) -> None:
        if interaction.user.id != self.player_active.id:
            return
        
        await interaction.response.defer()

        self.can_end_round = True
        round_shot: Round = self.revolver.fire()

        for child in self.walk_children():
            if child.label == 'Pass the gun':
                child.disabled = False
                break
        
        current_embed: discord.Embed = interaction.message.embeds[0]

        if round_shot == Round.LIVE:
            current_embed.set_footer(text=f"{self.player_active.display_name} Lost!")
            self.history.append('Fired(LIVE)')
            new_embed: discord.Embed = await self.setup_embed(current_embed)
            for child in self.children:
                child.disabled = True
            await self.player_active.timeout(datetime.timedelta(seconds=10))
        
        elif round_shot == Round.EMPTY:
            self.history.append('Fired(EMPTY)')
            
            new_embed: discord.Embed = await self.setup_embed(current_embed)
        
        await interaction.message.edit(embed=new_embed, view=self)
    

    @discord.ui.button(
        label='Spin',
        custom_id='button_spin',
        style=discord.ButtonStyle.secondary,
        row=0,
    )
    async def button_spin_callback(self, interaction: discord.Interaction, button: discord.Button) -> None:
        if interaction.user.id != self.player_active.id:
            return
        
        await interaction.response.defer()

        self.revolver.spin()
        self.history.append('Spun the cylinder')

        current_embed: discord.Embed = interaction.message.embeds[0]
        new_embed: discord.Embed = await self.setup_embed(current_embed)

        button.disabled = True
        await interaction.message.edit(embed=new_embed, view=self)


    @discord.ui.button(
        label='Pass the gun',
        custom_id='button_pass',
        style=discord.ButtonStyle.success,
        row=0,
        disabled=True
    )
    async def button_pass_callback(self, interaction: discord.Interaction, button: discord.Button) -> None:
        if interaction.user.id != self.player_active.id:
            return
        
        if not self.can_end_round:
            return
        
        await interaction.response.defer()

        self.can_end_round = False
        self.history = []
        

        self.player_active = self.player2 if self.player_active.id == self.player1.id else self.player1
        button.disabled = True
        current_embed: discord.Embed = interaction.message.embeds[0]

        new_embed: discord.Embed = await self.setup_embed(current_embed)
        await interaction.message.edit(embed=new_embed, view=self)



# @discord.ui.button(
#     label='check',
#     custom_id='button_check',
#     style=discord.ButtonStyle.success,
#     row=0,
# )
# async def button_check_callback(self, interaction: discord.Interaction, button: discord.Button) -> None:
#     await interaction.response.send_message(self.revolver.give_cylinder())


# if self.player_active.id == interaction.client.user.id:
#     await sleep(2.0)

#     round_shot: Round = self.revolver.fire()

#     current_embed: discord.Embed = interaction.message.embeds[0]
#     if round_shot == Round.LIVE:
#         current_embed.set_footer(text=f"{self.player_active.display_name} Lost!")
#         for child in self.children:
#             child.disabled = True
#         await interaction.message.edit(embed=current_embed, view=self)

#     elif round_shot == Round.EMPTY:

#         self.player_active: discord.Member = self.player2 if self.player_active.id == self.player1.id else self.player1

#         new_embed: discord.Embed = await self.setup_embed(current_embed)
#         await interaction.message.edit(embed=new_embed, view=self)