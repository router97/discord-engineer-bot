import asyncio
import datetime
from typing import Any

import discord


class MutesView(discord.ui.LayoutView):
    MEMBERS_TEXT_ID = 321

    def __init__(self, data: list[dict[str, Any]]) -> None:
        super().__init__()
        self.data: list[dict] = data

        container_items = []
        
        container_items.append(
            discord.ui.TextDisplay(
                '## Active Mutes List'
            )
        )
        container_items.append(
            discord.ui.Separator()
        )
        container_items.append(
            discord.ui.TextDisplay(self.get_text())
        )
        container_items.append(
            discord.ui.Separator()
        )
        container = discord.ui.Container(
            *container_items,
            accent_color=discord.Color.purple(),
        )
        self.add_item(container)
    

    def get_text(self) -> str:
        text = ''
        for i, subdata in enumerate(self.data):
            member: discord.Member = subdata['member']
            until: datetime.datetime = subdata['until']
            text += f"### \\#{i}. {member.mention} (ID: `{member.id}`)\n" 
            text += f"-# **Until:** <t:{int(until.timestamp())}:D> (<t:{int(until.timestamp())}:R>)\n"
        
        return text
