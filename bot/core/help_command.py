"""
This module contains the logic behind the help command.
"""
import discord
from discord.ext import commands

from .config import COMMAND_PREFIX


class SendBotHelpSelect(discord.ui.Select):
    """
    A select menu for the send_bot_help method, which provides help for the selected cog.
    """
    def __init__(self, help_command: commands.HelpCommand, cogs: list[commands.Cog]) -> None:
        """
        Initializes the select menu.

        :param help_command: The help command.
        :type help_command: commands.HelpCommand
        :param cogs: A list of cogs to select from.
        :type cogs: list[commands.Cog]
        """
        self.help_command: commands.HelpCommand = help_command
        self.cog_name_mapping: dict[str, commands.Cog] = {cog.qualified_name: cog for cog in cogs}

        options: list[discord.SelectOption] = [
            discord.SelectOption(
                label=cog.qualified_name,
                value=cog.qualified_name
            ) for cog in cogs
        ]

        super().__init__(
            placeholder="Select category...",
            options=options,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Callback function for the select menu. Is called when an item is selected

        :param interaction: The interaction.
        :type interaction: discord.Interaction
        :return: Nothing. Sends the help command for the cog selected.
        :rtype: None
        """
        await interaction.response.defer()

        picked_cog: commands.Cog = self.cog_name_mapping[self.values[0]]

        await self.help_command.send_cog_help(picked_cog)


class SendBotHelpView(discord.ui.View):
    """
    The view for the send_bot_help method.
    Has a select menu in which you can select a cog to view its help command.
    """
    def __init__(self, help_command: commands.HelpCommand, cogs: list[commands.Cog]) -> None:
        """
        Initializes the view.

        :param help_command: The help command.
        :type help_command: commands.HelpCommand
        :param cogs: A list of cogs to select from. (for the select menu)
        :type cogs: list[commands.Cog]
        """
        super().__init__()
        self.add_item(SendBotHelpSelect(help_command, cogs))


class CustomHelpCommand(commands.HelpCommand):
    def __init__(self) -> None:
        super().__init__()

    async def send_bot_help(self, mapping) -> None:
        embed: discord.Embed = discord.Embed(
            title='Available commands:',
            color=discord.Color.teal(),
            description='You can get detailed help information for every command'
                        f"by passing its name, for example: `{COMMAND_PREFIX}help ip`",
        )
        embed.set_thumbnail(url=self.context.bot.user.display_avatar.url)

        cogs_to_list: list[commands.Cog] = []
        for cog, cog_commands in mapping.items():
            if not cog:
                embed.add_field(
                    name=f"No Category:",
                    value=' '.join([f'`{COMMAND_PREFIX}{command.name}`' for command in cog_commands]),
                    inline=False,
                )
            else:
                cogs_to_list.append(cog)
                embed.add_field(
                    name=f"{cog.qualified_name} ({COMMAND_PREFIX}help {cog.qualified_name})",
                    value=' '.join([f'`{COMMAND_PREFIX}{command.name}`' for command in cog_commands]),
                    inline=False,
                )

        view: SendBotHelpView = SendBotHelpView(help_command=self, cogs=cogs_to_list)
        await self.get_destination().send(
            embed=embed,
            delete_after=120.0,
            allowed_mentions=discord.AllowedMentions.none(),
            view=view,
            silent=True,
        )

    async def send_cog_help(self, cog: commands.Cog) -> None:
        embed: discord.Embed = discord.Embed(
            title=f'Available commands of category {cog.qualified_name}:',
            color=discord.Color.teal(),
            description='You can get detailed help information for every command'
                        f"by passing its name, for example: `{COMMAND_PREFIX}help ip`",
        )
        embed.set_thumbnail(url=self.context.bot.user.display_avatar.url)

        for command in cog.get_commands():
            embed.add_field(
                name=COMMAND_PREFIX+command.qualified_name,
                value=command.description,
                inline=False,
            )

        await self.get_destination().send(
            embed=embed,
            delete_after=120.0,
            allowed_mentions=discord.AllowedMentions.none(),
            silent=True,
        )

    async def send_group_help(self, group) -> None:
        return await super().send_group_help(group)

    async def send_command_help(self, command) -> None:
        embed: discord.Embed = discord.Embed(
            color=discord.Color.teal(),
            description=command.description,
        )
        embed.set_author(name=f'Command "{COMMAND_PREFIX}{command.qualified_name}"')

        for parameter in command.clean_params.values():
            description = parameter.description
            if parameter.default:
                description += f'\nDefaults to {parameter.displayed_default}'

            embed.add_field(
                name=parameter.displayed_name,
                value=description,
                inline=False,
            )

        await self.get_destination().send(
            embed=embed,
            delete_after=120.0,
            allowed_mentions=discord.AllowedMentions.none(),
            silent=True,
        )
