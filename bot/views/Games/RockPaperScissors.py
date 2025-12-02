from random import choice
from enum import Enum
from dataclasses import dataclass
from typing import Callable, Awaitable

import discord


class GameResult(Enum):
    GAME_UNFINISHED = -1
    TIE = 0
    PLAYER1_WON = 1
    PLAYER2_WON = 2


@dataclass(frozen=True)
class Pick:
    name: str
    emoji: str


ROCK: Pick = Pick(name='rock', emoji='🗿')
PAPER: Pick = Pick(name='paper', emoji='📄')
SCISSORS: Pick = Pick(name='scissors', emoji='✂️')

PICKS: list[Pick] = [ROCK, PAPER, SCISSORS]


class RockPaperScissorsSelect(discord.ui.Select):
    def __init__(self, process_interaction: Callable[[discord.Interaction, Pick], Awaitable[None]]) -> None:
        self.process_interaction = process_interaction
        options: list[discord.SelectOption] = [
            discord.SelectOption(label=pick.name.capitalize(), value=pick.name, emoji=pick.emoji) for pick in PICKS
        ]
        super().__init__(placeholder="Choose", max_values=1, min_values=1, options=options)
    
    
    async def callback(self, interaction: discord.Interaction) -> None:
        selected_pick = next(pick for pick in PICKS if pick.name == self.values[0])
        await self.process_interaction(interaction, selected_pick)


class RockPaperScissorsView(discord.ui.View):
    def __init__(self, user1: discord.Member, user2: discord.Member) -> None:
        super().__init__() 
        self.user1 = user1
        self.user2 = user2
        self.pick = {}
        self.__winning_combinations = {
            (ROCK, PAPER): self.user2,
            (ROCK, SCISSORS): self.user1,
            (PAPER, ROCK): self.user1,
            (PAPER, SCISSORS): self.user2,
            (SCISSORS, ROCK): self.user2,
            (SCISSORS, PAPER): self.user1,
        }
        self.add_item(RockPaperScissorsSelect(self.process_interaction))
    
    
    async def setup_embed(self, embed_to_update: discord.Embed = None) -> discord.Embed:
        if embed_to_update is None:
            embed: discord.Embed = discord.Embed(title='Rock, Paper, Scissors', color=discord.Color.red())
            embed.add_field(name=self.user1.display_name, value='Not Ready')
            embed.add_field(name=self.user2.display_name, value='Not Ready')
            return embed
        
        pick1: Pick | None = self.pick.get(self.user1)
        pick2: Pick | None = self.pick.get(self.user2)
        embed_to_update.set_field_at(0, name=self.user1.display_name, value=pick1.emoji if pick1 else 'Not Ready')
        embed_to_update.set_field_at(1, name=self.user2.display_name, value=pick2.emoji if pick2 else 'Not Ready')
        return embed_to_update
    
    
    async def game_logic(self) -> GameResult:
        pick1: Pick | None = self.pick.get(self.user1)
        pick2: Pick | None = self.pick.get(self.user2)
        if not pick1 or not pick2:
            return GameResult.GAME_UNFINISHED
        if pick1 == pick2:
            return GameResult.TIE
        if (pick1, pick2) in self.__winning_combinations:
            return GameResult.PLAYER2_WON if self.__winning_combinations[(pick1, pick2)] == self.user2 else GameResult.PLAYER1_WON


    async def process_interaction(self, interaction: discord.interactions.Interaction, pick: Pick):
        if interaction.user.id not in (self.user1.id, self.user2.id):
            return
        
        await interaction.response.defer()
        
        self.pick[interaction.user] = pick
        
        if self.user2 == interaction.client.user:
            bot_pick: Pick = choice(PICKS)
            self.pick[self.user2] = bot_pick
        
        current_embed: discord.Embed = await self.setup_embed(interaction.message.embeds[0])
        
        if len(self.pick) != 2:
            await interaction.message.edit(embed=current_embed)
            return
        
        result: GameResult = await self.game_logic()
        
        if result == GameResult.PLAYER1_WON:
            result_text: str = f"{self.user1.display_name} Won!"
        elif result == GameResult.PLAYER2_WON:
            result_text: str = f"{self.user2.display_name} Won!"
        elif result == GameResult.TIE:
            result_text: str = "It's a tie!"
        elif result == GameResult.GAME_UNFINISHED:
            result_text: str = "Game unfinished."
        
        current_embed.set_footer(text=result_text)
        
        for child in self.children:
            if type(child) == RockPaperScissorsSelect:
                child.disabled = True
        
        await interaction.message.edit(embed=current_embed, view=self)
