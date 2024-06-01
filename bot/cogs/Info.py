"""
Info
====

This cog module contains mostly commands that display information about something.
For example, displaying information about a certain user or a guild.
"""

import datetime

import discord
from discord.ext import commands

from core.bot import bot


class Info(commands.Cog):
    """Information commands"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="serverinfo", description="Get server stats")
    async def serverinfo(self, ctx: commands.Context):
        """Get server stats"""
        
        # Fetch the server
        server = ctx.guild
        
        # Create the embed
        embed = discord.Embed(title=f":bar_chart:   **{server.name}**", 
                              description=f"""
                              *{server.description if server.description else 'No description available'}*\n
                              """,
                              color = discord.Color.red())
        embed.set_author(name=f"Requested by - {ctx.author}", icon_url=f"{ctx.author.avatar if ctx.author.avatar else ctx.author.default_avatar}")
        embed.set_footer(text=f"{server.name} stats", icon_url=f"{server.icon if server.icon else ''}")
        embed.set_image(url=server.icon.url if server.icon else None)
        
        
        # Line 1
        embed.add_field(name=':hourglass:   Created On', value=f"{server.created_at.year}-{server.created_at.month}-{server.created_at.day} | {server.created_at.hour}:{server.created_at.minute}:{server.created_at.second}", inline=False)
        
        
        # Line 2
        embed.add_field(name=':crown:   Guild Owner', value=f"<@{server.owner_id}>", inline=False)
        
        
        # Line 3
        embed.add_field(name='Total Members', value=f"{server.member_count}")
        
        real_members = [member for member in server.members if member.bot is False]
        embed.add_field(name='Total Real Members', value=f"{len(real_members)}")
        
        bot_members = [member for member in server.members if member.bot]
        embed.add_field(name='Total Bots', value=f"{len(bot_members)}")
        
        
        # Line 4
        embed.add_field(name='Total Channels', value=f"{len([channel for channel in server.channels if not isinstance(channel, discord.CategoryChannel)])}")
        
        text_channels = [channel for channel in server.channels if isinstance(channel, discord.TextChannel)]
        embed.add_field(name='Total Text Channels', value=f"{len(text_channels)}")
        
        voice_channels = [channel for channel in server.channels if isinstance(channel, discord.VoiceChannel)]
        embed.add_field(name='Total Voice Channels', value=f"{len(voice_channels)}")
        
        
        # Send the embed
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="user", description="Get user stats")
    async def user(self, ctx: commands.Context, member: commands.MemberConverter = commands.parameter(default=None, description="The user you want to view.", displayed_default="Yourself", displayed_name="User")):
        """Get member stats."""
        member = member or ctx.author
        member_avatar = member.avatar if member.avatar else member.default_avatar
        author_avatar = ctx.author.avatar if ctx.author.avatar else ctx.author.default_avatar
        
        member_roles = [f"<@&{role.id}>" for role in member.roles if role.id if role.id != 982052021957976114]
        
        embed = discord.Embed(title=f":bar_chart:   **{member.display_name}**", 
                              description=f"""
                              *{', '.join(member_roles)}*\n
                              """,
                              color = member.accent_color)
        
        embed.set_author(name=f"Requested by - {ctx.author}", icon_url=f"{author_avatar}")
        embed.set_footer(text=f"{member.name} stats", icon_url=f"{member_avatar.url}")
        embed.set_image(url=member_avatar.url)
        
        embed.add_field(name=':hourglass:   Created On', value=f"{member.created_at.year}-{member.created_at.month}-{member.created_at.day} | {member.created_at.hour}:{member.created_at.minute}:{member.created_at.second}", inline=False)
        
        await ctx.reply(embed=embed, silent=True)
    
    @commands.hybrid_command(name="avatar", description="Fetch a user's avatar")
    async def avatar(self, ctx: commands.Context, member: commands.MemberConverter = commands.parameter(default=None, description="The user you want to view.", displayed_default="Yourself", displayed_name="User")):
        """Fetch a user's avatar"""
        
        member: discord.Member = member or ctx.author
        
        # Fetch the member's avatar
        member_avatar: discord.Asset = member.display_avatar or member.default_avatar
        
        embed = discord.Embed(color=discord.Color.teal(), title=f"Avatar of {member.display_name}")
        embed.set_image(url=member_avatar.url)
        
        # Send the message
        await ctx.reply(embed=embed, delete_after=60.0, ephemeral=True, silent=True)
    
    @commands.hybrid_command(name="db", description="Check if the user is in the database, if so, provide the data.")
    async def db(self, ctx: commands.Context, member: commands.MemberConverter = commands.parameter(default=None, description="The user you want to query.", displayed_default= 'Yourself', displayed_name="User")):
        """Bigger description"""
        user_to_select = member if member else ctx.author
        user_id = user_to_select.id
        user = await ctx.bot.db.fetchrow('SELECT * FROM users WHERE id = $1', user_id)
        
        embed = discord.Embed(title=f'SELECT * FROM users WHERE id = {user_id}', timestamp=datetime.datetime.now())
        embed.set_footer(text=user_to_select.display_name, icon_url=user_to_select.display_avatar.url)
        
        if not user:
            embed.description = 'User not found'
            embed.color = discord.Color.red()
        else:
            embed.color = discord.Color.teal()
            for key, value in user.items():
                embed.add_field(name=key, value=value, inline=True)
        
        await ctx.reply(embed=embed, delete_after=60.0, ephemeral=True, silent=True)
        await ctx.message.delete()


@bot.tree.context_menu(name='Show Info')
async def user_info_context_menu(interaction: discord.Interaction, user: discord.Member):
    """Get member stats."""
        
    member_avatar = user.avatar if user.avatar else user.default_avatar
    author_avatar = interaction.user.avatar if interaction.user.avatar else interaction.user.default_avatar
    
    member_roles = [f"<@&{role.id}>" for role in user.roles if role.id if role.id != 982052021957976114]
    
    embed = discord.Embed(title=f":bar_chart:   **{user.display_name}**", 
                            description=f"""
                            *{', '.join(reversed(member_roles))}*\n
                            """,
                            color = user.accent_color)
    
    embed.set_author(name=f"Requested by - {interaction.user}", icon_url=f"{author_avatar}")
    embed.set_footer(text=f"{user.name} stats", icon_url=f"{member_avatar.url}")
    embed.set_image(url=member_avatar.url)
    
    embed.add_field(name=':hourglass:   Created On', value=f"{user.created_at.year}-{user.created_at.month}-{user.created_at.day} | {user.created_at.hour}:{user.created_at.minute}:{user.created_at.second}", inline=False)
    
    await interaction.response.send_message(embed=embed, silent=True, ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(Info(bot))