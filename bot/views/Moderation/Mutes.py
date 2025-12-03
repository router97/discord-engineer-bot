import discord
import datetime
import asyncio


class MutesView(discord.ui.View):
    BACK_BUTTON_LABEL = 'BACK'
    NEXT_BUTTON_LABEL = 'NEXT'

    def __init__(self, *, timeout = 180, data, message: discord.Message):
        super().__init__(timeout=timeout)
        self.message: discord.Message = message
        self.data: list[dict] = data
        self.page = 0
        self.pagesize = 1
        self.data_length = len(data)
        self.max_page = self.data_length // self.pagesize

        embed = self.setup_embed()
        asyncio.create_task(message.edit(embed = embed, view=self, content=None))
    
    def setup_embed(self):
        embed = discord.Embed(title='Mutes')
        embed.set_footer(text=f'Page: {self.page}')
        temp_pagesize = self.pagesize
        try:
            data_display = self.data[temp_pagesize * self.page: temp_pagesize * self.page + temp_pagesize]
        except IndexError:
            good = False
            while not good:
                temp_pagesize -= 1
                try:
                    data_display = self.data[temp_pagesize * self.page: temp_pagesize * self.page + temp_pagesize]
                except:
                    pass
                else:
                    good = True

        for i, subdata in enumerate(data_display):
            member: discord.Member = subdata['member']
            until: datetime.datetime = subdata['until']
            embed.add_field(name=f"#{i}. {member.display_name} (ID: `{member.id}`)", value=f"Until: <t:{int(until.timestamp())}:D> (<t:{int(until.timestamp())}:R>)")
        
        return embed


    @discord.ui.button(
        label=BACK_BUTTON_LABEL,
        custom_id='button_previous',
        style=discord.ButtonStyle.primary,
        row=0,
    )
    async def button_previous_callback(self, interaction: discord.Interaction, button: discord.Button) -> None:
        await interaction.response.defer()
        self.page -= 1
        for child in self.children:
            child.disabled = False
        if self.page <= 0:
            button.disabled = True
        embed = self.setup_embed()
        await interaction.message.edit(view=self, embed=embed)


    @discord.ui.button(
        label=NEXT_BUTTON_LABEL,
        custom_id='button_next',
        style=discord.ButtonStyle.primary,
        row=0,
    )
    async def button_next_callback(self, interaction: discord.Interaction, button: discord.Button) -> None:
        await interaction.response.defer()
        self.page += 1
        for child in self.children:
            child.disabled = False
        if self.page >= self.max_page -1:
            button.disabled = True
        
        embed = self.setup_embed()
        await interaction.message.edit(view=self, embed=embed)
    
    
