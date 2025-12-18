import asyncio
import datetime
from typing import Any

import discord


class LeadersView(discord.ui.LayoutView):
    MEMBERS_TEXT_ID = 321

    def __init__(self, data: list[dict[str, Any]]) -> None:
        super().__init__()
        self.data: list[dict] = data

        container_items = []
        
        container_items.append(
            discord.ui.TextDisplay(
                '## Leaders'
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
        for item in self.data:
            member: str = item['user']
            text += f"### {member} ({item['chat_experience']} XP)\n" 
        
        return text
