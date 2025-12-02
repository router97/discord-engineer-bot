import discord


class TicTacToeView(discord.ui.View):
    _button_data = [
            ('1', 0),
            ('2', 0),
            ('3', 0),
            ('4', 1),
            ('5', 1),
            ('6', 1),
            ('7', 2),
            ('8', 2),
            ('9', 2),
        ]
    EMPTY_SYMBOL = '⬜'
    CROSS_SYMBOL = '❌'
    CIRCLE_SYMBOL = '⭕'
    
    async def setup_embed(self) -> discord.Embed:
        embed = discord.Embed(title='Tic-tac-toe', color=discord.Color.red())
        embed.set_author(name=f"{self.user1.display_name} vs {self.user2.display_name}")
        embed.add_field(name='Board', value=':white_large_square::white_large_square::white_large_square:\n'*3)
        return embed
    
    def __init__(self, user1: discord.Member, user2: discord.Member):
        super().__init__()
        self.user1 = user1
        self.user2 = user2
        self.player = user1
        self.board_map = {str(i): self.EMPTY_SYMBOL for i in range(1, 10)}
        for label, row in self._button_data:
            button = discord.ui.Button(label=label, row=row, style=discord.ButtonStyle.primary, custom_id=label)
            button.callback = self.callback
            self.add_item(button)
            
    async def retry(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user not in (self.user1, self.user2):
            return
        
        self.player = self.user1
        
        self.board_map = {str(i): self.EMPTY_SYMBOL for i in range(1, 10)}
        
        embed = interaction.message.embeds[0]
        
        embed.set_field_at(0, name='Board', value=':white_large_square::white_large_square::white_large_square:\n'*3)
        
        for callback in self.children:
            callback.disabled = False
        
        self.button_retry_callback.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def game_logic(self, board_map: str):
        board_map_line_split = board_map.splitlines()
        
        board_map_horizontal = [[i for i in el] for el in board_map_line_split]
        
        board_map_vertical = [[el[counter] for el in board_map_line_split] for counter in range(3)]
        
        board_map_cross1 = [[el[counter] for el, counter in zip(board_map_line_split, range(3))]]
        board_map_cross2 = [[el[counter] for el, counter in zip(board_map_line_split, range(2, -1, -1))]]
        
        for checking in (board_map_horizontal, board_map_vertical, board_map_cross1, board_map_cross2):
            for check in checking:
                if check == [self.CROSS_SYMBOL, self.CROSS_SYMBOL, self.CROSS_SYMBOL]:
                    return self.user1.id
                elif check == [self.CIRCLE_SYMBOL, self.CIRCLE_SYMBOL, self.CIRCLE_SYMBOL]:
                    return self.user2.id
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.player:
            return
        
        button = next(item for item in self.children if item.custom_id == interaction.data['custom_id'])
        
        self.board_map.update({button.label: self.CROSS_SYMBOL if interaction.user == self.user1 else self.CIRCLE_SYMBOL})
    
        embed = interaction.message.embeds[0]
        
        board_map_updated = list(self.board_map.values())
        board_map_updated = '\n'.join([''.join(board_map_updated[counter:counter+3]) for counter in range(0, len(board_map_updated), 3)])
        
        embed.set_field_at(0, name='Board', value=board_map_updated)
    

        button.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)
        
        outcome = await self.game_logic(board_map_updated)
        
        if outcome:
            await interaction.message.channel.send(f"<@{outcome}> won!")
            for callback in self.children:
                callback.disabled = True
            self.button_retry_callback.disabled = False
            return await interaction.message.edit(view=self)

        if self.EMPTY_SYMBOL not in board_map_updated:
            await interaction.message.channel.send(f"draw!")
            for callback in self.children:
                callback.disabled = True
            self.button_retry_callback.disabled = False
            return await interaction.message.edit(view=self)
        
        self.player = self.user1 if self.player == self.user2 else self.user2
    
    @discord.ui.button(label='Retry', row=3, style=discord.ButtonStyle.secondary, disabled=True)
    async def button_retry_callback(self, interaction: discord.interactions.Interaction, button: discord.ui.Button):
        await self.retry(interaction, button)