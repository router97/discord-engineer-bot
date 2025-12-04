import discord
import datetime
import asyncio




class PageButtons(discord.ui.ActionRow):
    BACK_BUTTON_LABEL = 'BACK'
    NEXT_BUTTON_LABEL = 'NEXT'

    def __init__(self, view: 'MutesView') -> None:
        self.__view = view
        super().__init__()
    

    @discord.ui.button(
        label=BACK_BUTTON_LABEL,
        custom_id='button_previous',
        style=discord.ButtonStyle.primary,
        row=0,
    )
    async def button_previous_callback(self, interaction: discord.Interaction, button: discord.Button) -> None:
        if self.__view.page > self.__view.max_page:
            self.__view.page -= 1
        else:
            await interaction.response.defer()
            return
        
        self.__view.members_text.content = self.__view.get_text()
        await interaction.response.edit_message(view=self.__view)


    @discord.ui.button(
        label=NEXT_BUTTON_LABEL,
        custom_id='button_next',
        style=discord.ButtonStyle.primary,
        row=0,
    )
    async def button_next_callback(self, interaction: discord.Interaction, button: discord.Button) -> None:
        if self.__view.page < self.__view.max_page:
            self.__view.page += 1
        else:
            await interaction.response.defer()
            return

        self.__view.members_text.content = self.__view.get_text()
        await interaction.response.edit_message(view=self.__view)


class MutesView(discord.ui.LayoutView):
    MEMBERS_TEXT_ID = 321

    def __init__(self, data: list[dict]) -> None:
        super().__init__()
        self.data: list[dict] = data
        self.page = 0
        self.pagesize = 1
        self.data_length = len(data)
        self.max_page = (self.data_length // self.data_length) - 1

        self.members_text = discord.ui.TextDisplay(self.get_text())
        self.buttons = PageButtons(self)

        self.buttons = PageButtons(self)
        container = discord.ui.Container(
            self.members_text,
            discord.ui.Separator(), 
            self.buttons, 
            accent_color=discord.Color.purple(),
            )
        self.add_item(container)
    
    def get_text(self) -> str:
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

        text = ''
        for i, subdata in enumerate(data_display):
            member: discord.Member = subdata['member']
            until: datetime.datetime = subdata['until']
            text += f"#{i}. {member.display_name} (ID: `{member.id}`) Until: <t:{int(until.timestamp())}:D> (<t:{int(until.timestamp())}:R>)\n"
        
        return text
