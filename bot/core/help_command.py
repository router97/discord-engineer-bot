import asyncio

import discord
from discord.ext import commands

from .config import COMMAND_PREFIX

# TODO: hide hidden commands and cogs
# TODO: Add pagination (not really necessary, just to minmax)

BUTTON_LABEL = '➤'


class SendBotHelpButton(discord.ui.Button):
    def __init__(self, help_command: commands.HelpCommand, mapping, *, label=BUTTON_LABEL):
        self.help_command = help_command
        self.mapping = mapping
        super().__init__(style=discord.ButtonStyle.primary, label=label)
    
    async def callback(self, interaction: discord.Interaction):
        asyncio.gather(
            self.help_command.send_bot_help(self.mapping),
            interaction.message.delete()
        )


class SendCogHelpButton(discord.ui.Button):
    def __init__(self, help_command: commands.HelpCommand, cog: commands.Cog, *, label=BUTTON_LABEL):
        self.help_command = help_command
        self.cog = cog
        super().__init__(style=discord.ButtonStyle.primary, label=label)
    
    async def callback(self, interaction: discord.Interaction):
        asyncio.gather(
            self.help_command.send_cog_help(self.cog),
            interaction.message.delete()
        )


class SendCommandHelpButton(discord.ui.Button):
    def __init__(self, help_command: commands.HelpCommand, command: commands.Command, *, label=BUTTON_LABEL):
        self.help_command = help_command
        self.command = command
        super().__init__(style=discord.ButtonStyle.primary, label=label)
    
    async def callback(self, interaction: discord.Interaction):
        asyncio.gather(
            self.help_command.send_command_help(self.command),
            interaction.message.delete()
        )


class SendBotHelpView(discord.ui.LayoutView):
    def __init__(self, help_command: commands.HelpCommand, mapping: dict[commands.Cog | None, list[commands.Command]]) -> None:
        self.help_command = help_command
        self.mapping = mapping
        super().__init__()

        self.sections: list[discord.ui.Section] = []
        for cog, _commands in mapping.items():
            if cog is None:
                continue

            button = SendCogHelpButton(help_command, cog)

            self.sections.append(
                discord.ui.Section(
                    discord.ui.TextDisplay(
                        f"### {cog.qualified_name}\n"
                        f"{' '.join([f'`{COMMAND_PREFIX}{command.name}`' for command in _commands])}"
                    ),
                    accessory=button,
                )
            )
        container_items = []

        container_items.append(
            discord.ui.TextDisplay(
                content = '## Available commands:\n'
                          'You can get detailed help information for every command '
                          f"by passing its name, \nfor example: `{COMMAND_PREFIX}help ip`"
            )
        )
        container_items.append(
            discord.ui.Separator()
        )

        for section in self.sections:
            container_items.append(section)
            container_items.append(
                discord.ui.Separator()
            )
        container_items.pop()

        container = discord.ui.Container(
            *container_items,
            accent_color=discord.Color.pink(),
        )
        self.add_item(container)


class SendCogHelpView(discord.ui.LayoutView):
    def __init__(self, help_command: commands.HelpCommand, cog: commands.Cog) -> None:
        self.help_command = help_command
        self.cog = cog
        super().__init__()

        self.sections: list[discord.ui.Section] = []
        for command in cog.walk_commands():
            button = SendCommandHelpButton(help_command, command)

            self.sections.append(
                discord.ui.Section(
                    discord.ui.TextDisplay(
                        f"### {COMMAND_PREFIX}{command.qualified_name}\n"
                        f"{command.description}"
                    ),
                    accessory=button,
                )
            )
        container_items = []

        container_items.append(
            discord.ui.TextDisplay(
                content = f'## Available commands in category {cog.qualified_name}:\n'
                          'You can get detailed help information for every command '
                          f"by passing its name, \nfor example: `{COMMAND_PREFIX}help ip`"
            )
        )
        container_items.append(
            discord.ui.ActionRow(
                SendBotHelpButton(help_command, help_command.get_bot_mapping(), label='⮜ All commands')
            )
        )
        container_items.append(
            discord.ui.Separator()
        )

        for section in self.sections:
            container_items.append(section)
            container_items.append(
                discord.ui.Separator()
            )
        container_items.pop()

        container = discord.ui.Container(
            *container_items,
            accent_color=discord.Color.pink(),
        )
        self.add_item(container)


class SendCommandHelpView(discord.ui.LayoutView):
    def __init__(self, help_command: commands.HelpCommand, command: commands.Command) -> None:
        self.help_command = help_command
        self.command = command
        super().__init__()

        container_items = []

        container_items.append(
            discord.ui.TextDisplay(
                content = f'## Command `{command.qualified_name}`\n'
                          f'{command.description}'
            )
        )
        container_items.append(
            discord.ui.ActionRow(
                SendCogHelpButton(help_command, command.cog, label=f'⮜ {command.cog.qualified_name}')
            )
        )
        container_items.append(
            discord.ui.Separator()
        )
        for parameter in command.clean_params.values():
            container_items.append(
                discord.ui.TextDisplay(
                    content = f'### {parameter.displayed_name}\n'
                            f'{parameter.description}'
                )
            )
            container_items.append(
                discord.ui.Separator()
            )
        container_items.pop()
        

        container = discord.ui.Container(
            *container_items,
            accent_color=discord.Color.pink(),
        )
        self.add_item(container)


class CustomHelpCommand(commands.HelpCommand):
    def __init__(self) -> None:
        super().__init__()


    async def send_bot_help(self, mapping: dict[commands.Cog | None, list[commands.Command]]) -> None:
        view = SendBotHelpView(self, mapping)
        await self.get_destination().send(
            delete_after=120.0,
            allowed_mentions=discord.AllowedMentions.none(),
            view=view,
            silent=True,
        )

    async def send_cog_help(self, cog: commands.Cog) -> None:
        view = SendCogHelpView(self, cog)
        await self.get_destination().send(
            delete_after=120.0,
            allowed_mentions=discord.AllowedMentions.none(),
            view=view,
            silent=True,
        )


    async def send_command_help(self, command: commands.Command) -> None:
        view = SendCommandHelpView(self, command)
        await self.get_destination().send(
            delete_after=120.0,
            allowed_mentions=discord.AllowedMentions.none(),
            view=view,
            silent=True,
        )
