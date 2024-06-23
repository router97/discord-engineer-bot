"""
Info
====

This cog module contains mostly commands that display information about something.
For example, displaying information about a certain user or a guild.
"""
import unicodedata
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from numerize.numerize import numerize


class Info(commands.Cog):
    """
    A cog with information-related commands.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="serverinfo", description="Get information about the server.")
    async def serverinfo(
            self,
            ctx: commands.Context,
    ) -> None:
        """
        Replies with an embed, containing fields with information about the server.

        :param ctx: The context in which the command is invoked.
        :type ctx: commands.Context
        :return: None. The function only sends a Discord message, doesn't return anything in the code.
        :rtype: None
        """
        await ctx.defer(ephemeral=True)
        guild: discord.Guild = ctx.guild

        embed: discord.Embed = discord.Embed(
            title=f"Information about **{guild.name}**",
            description=guild.description,
            color=discord.Color.teal(),
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.set_image(url=guild.banner.url if guild.banner else None)
        embed.set_footer(text=f'ID: {guild.id}')

        total_members: Optional[int] = guild.member_count
        real_members: int = len([member for member in guild.members if not member.bot])
        bot_members: int = total_members - real_members
        embed.add_field(
            name='Members:',
            value=f"Total: **{numerize(total_members)}**"
                  f"\nMembers: **{numerize(real_members)}**"
                  f"\nBots: **{numerize(bot_members)}**",
            inline=True,
        )

        online_members = sum(
            1 for member in guild.members if not member.bot and member.status != discord.Status.offline)
        offline_members = real_members - online_members
        embed.add_field(
            name='By Status:',
            value=f"Online: **{numerize(online_members)}**"
                  f"\nOffline: **{numerize(offline_members)}**",
            inline=True,
        )

        total_channels: int = 0
        text_channels: int = 0
        voice_channels: int = 0
        forum_channels: int = 0
        announcement_channels: int = 0
        for channel in guild.channels:
            if isinstance(channel, discord.CategoryChannel):
                continue

            total_channels += 1

            if isinstance(channel, discord.VoiceChannel):
                voice_channels += 1

            elif isinstance(channel, discord.TextChannel):
                if channel.is_news():
                    announcement_channels += 1
                else:
                    text_channels += 1

            elif isinstance(channel, discord.ForumChannel):
                forum_channels += 1

        embed.add_field(
            name='Channels:',
            value=f"Total: **{numerize(total_channels)}**"
                  f"\nText: **{numerize(text_channels)}**"
                  f"\nForum: **{numerize(forum_channels)}**"
                  f"\nVoice: **{numerize(voice_channels)}**"
                  f"\nAnnouncement: **{numerize(announcement_channels)}**",
            inline=True,
        )

        embed.add_field(
            name='Owner:',
            value=guild.owner.name,
            inline=True,
        )

        embed.add_field(
            name='Verification Level:',
            value=str(guild.verification_level).title(),
            inline=True,
        )

        created_at: int = round(guild.created_at.timestamp())
        embed.add_field(
            name='Created on:',
            value=f'<t:{created_at}:D>\n<t:{created_at}:R>',
            inline=True,
        )

        await ctx.reply(
            embed=embed,
            silent=True,
            ephemeral=True,
            delete_after=60.0,
            allowed_mentions=discord.AllowedMentions.none(),
        )
        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.NotFound, discord.HTTPException):
            pass

    @commands.hybrid_command(name="user", description="Get information about a user.")
    async def user(
            self,
            ctx: commands.Context,
            member: commands.MemberConverter = commands.parameter(
                default=None,
                description="The user you want to inspect.",
                displayed_default="Yourself",
                displayed_name="User",
            ),
    ) -> None:
        """
        Replies with an embed, containing information about a user.

        :param ctx: The context in which the command is invoked.
        :type ctx: commands.Context
        :param member:
        :type member:
        :return: None. The function only sends a Discord message, doesn't return anything in the code.
        :rtype: None
        """
        await ctx.defer(ephemeral=True)
        member: discord.Member = member or ctx.author

        avatar: discord.Asset = member.display_avatar
        registered_at: int = round(member.created_at.timestamp())
        joined_at: int = round(member.joined_at.timestamp())

        embed: discord.Embed = discord.Embed(
            color=discord.Color.teal(),
        )
        embed.set_author(name=f"Information about {member.display_name}")
        embed.set_footer(text=f"ID: {member.id}")
        embed.set_thumbnail(url=avatar.url or None)
        embed.set_image(url=member.banner.url if member.banner else None)

        embed.add_field(name='Username:', value=member.name, inline=True)
        embed.add_field(name='Status:', value=str(member.status).title(), inline=True)
        embed.add_field(name='Joined at:', value=f"<t:{joined_at}:D> (<t:{joined_at}:R>)", inline=True)
        embed.add_field(name='Registered at:', value=f"<t:{registered_at}:D> (<t:{registered_at}:R>)", inline=True)

        await ctx.reply(
            embed=embed,
            silent=True,
            ephemeral=True,
            delete_after=60.0,
            allowed_mentions=discord.AllowedMentions.none(),
        )
        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.NotFound, discord.HTTPException):
            pass

    @commands.hybrid_command(name="avatar", description="Fetch a user's avatar")
    async def avatar(
            self,
            ctx: commands.Context,
            member: commands.MemberConverter = commands.parameter(
                default=None,
                description="The user, whose avatar you want to fetch.",
                displayed_default="Yourself",
                displayed_name="User",
            ),
    ) -> None:
        """
        Fetches a user's avatar.

        :param ctx: The context in which the command is invoked.
        :type ctx: commands.Context
        :param member: The user you want to view.
        :type member: commands.MemberConverter
        :return: The function only sends a Discord message, doesn't return anything in the code.
        :rtype: None
        """
        await ctx.defer(ephemeral=True)

        member: discord.Member = member or ctx.author

        embed = discord.Embed(
            color=discord.Color.teal(),
            title=f"Avatar of {member.display_name}",
        )
        embed.set_image(url=member.display_avatar.url)

        await ctx.reply(
            embed=embed,
            silent=True,
            ephemeral=True,
            delete_after=60.0,
            allowed_mentions=discord.AllowedMentions.none(),
        )
        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.NotFound, discord.HTTPException):
            pass

    @commands.hybrid_command(name="emote", description="Display information about an emote.")
    async def emote(
            self,
            ctx: commands.Context,
            emote: str = commands.parameter(
                description='The emote you want to inspect.',
                displayed_name='Emote',
            )
    ) -> None:
        """
        Replies with an embed, containing information about an emote(or character).

        :param ctx: The context in which the command is invoked.
        :type ctx: commands.Context
        :param emote: The emote(or character) you want to inspect.
        :type emote: str
        :return: None. The function only sends a Discord message, doesn't return anything in the code.
        :rtype: None
        """
        await ctx.defer(ephemeral=True)

        embed: discord.Embed = discord.Embed()

        try:
            custom_emoji = await commands.EmojiConverter().convert(ctx, emote)
        except commands.errors.BadArgument:
            embed.title = 'Emoji/Character Info:'
            embed.colour = discord.Color.teal()
            embed.description = "\n".join(
                [f"`\\u{ord(char):04X}` `{char}` *{unicodedata.name(char)}*" for char in emote]
            )
        else:
            embed.title = f'Emote "{custom_emoji.name}":'
            embed.url = custom_emoji.url
            embed.colour = discord.Color.teal()
            embed.set_image(url=custom_emoji.url)
            embed.set_footer(text=f'ID: {custom_emoji.id}')
        finally:
            if len(embed) > 6000:
                embed.title = 'Error!'
                embed.colour = discord.Color.red()
                embed.description = "Your input is too long! ||Embed size exceeds 6000, cannot send.||"

        await ctx.reply(
            embed=embed,
            silent=True,
            ephemeral=True,
            delete_after=60.0,
            allowed_mentions=discord.AllowedMentions.none(),
        )
        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.NotFound, discord.HTTPException):
            pass


async def user_info_context_menu_callback(interaction: discord.Interaction, user: discord.Member) -> None:
    """
    Replies with an embed, containing information about a user.

    :param interaction: The interaction with the context menu.
    :type interaction: discord.Interaction
    :param user: The user you want to inspect.
    :type user: discord.Member
    :return: None. The function only sends a Discord message, doesn't return anything in the code.
    :rtype: None
    """
    registered_at: int = round(user.created_at.timestamp())
    joined_at: int = round(user.joined_at.timestamp())

    embed: discord.Embed = discord.Embed(
        color=discord.Color.teal(),
    )
    embed.set_author(name=f"Information about {user.display_name}")
    embed.set_footer(text=f"ID: {user.id}")
    embed.set_thumbnail(url=user.display_avatar or None)
    embed.set_image(url=user.banner.url if user.banner else None)

    embed.add_field(name='Username:', value=user.name, inline=True)
    embed.add_field(name='Status:', value=str(user.status).title(), inline=True)
    embed.add_field(name='Joined at:', value=f"<t:{joined_at}:D> (<t:{joined_at}:R>)", inline=True)
    embed.add_field(name='Registered at:', value=f"<t:{registered_at}:D> (<t:{registered_at}:R>)", inline=True)

    await interaction.response.send_message(
        embed=embed,
        silent=True,
        ephemeral=True,
        delete_after=60.0,
        allowed_mentions=discord.AllowedMentions.none(),
    )


def setup(bot: commands.Bot):
    bot.add_cog(Info(bot))

    user_info_context_menu = app_commands.ContextMenu(
        name='Show Info',
        callback=user_info_context_menu_callback,
    )
    bot.tree.add_command(user_info_context_menu)
