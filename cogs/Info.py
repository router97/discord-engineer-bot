import json

import discord
from discord.ext import commands

from bot import bot


class Info(commands.Cog):
    """Information commands"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command()
    async def sg(self, ctx: commands.Context, *suggestion_tuple: str):
        """Make a suggestion related to the bot"""
        
        # Format the suggestion
        suggestion = ' '.join(suggestion_tuple)
        
        # Get all the suggestions
        with open("data/suggestions.json", "r", encoding="utf-8") as fl:
            all_dict = json.load(fl)
        
        # Get the keys
        user_key = str(ctx.author.id)
        all_dict_keys = all_dict.keys()
        
        # Add the suggestion
        if user_key in all_dict_keys:
            all_dict[user_key].append(suggestion)
        else:
            all_dict[user_key] = [suggestion,]
        
        # Dump the updated suggestions into the file
        with open("data/suggestions.json", "w", encoding="utf-8") as fl:
            json.dump(all_dict, fl, indent=4)
        
        await ctx.reply('got it', ephemeral=True)
    
    @commands.hybrid_command(name="sgs", description="Shows all the suggestions")
    async def sgs(self, ctx: commands.Context):
        """Shows all the suggestions"""
        
        # Reading the file
        with open("data/suggestions.json", "r", encoding="utf-8") as fl:
            suggestions_dict = json.load(fl)
        
        # Creating an empty list
        sgs = []
        
        # Going through member's id and their suggestions
        sgs = [f'# <@{member_id}>\n' + '\n'.join([f'- {suggestion}' for suggestion in suggestions]) 
               for member_id, suggestions in suggestions_dict.items()]
        
        # Joining everything with a new line
        sgs_message = "\n".join(sgs)
        
        # Sending the message
        await ctx.reply(sgs_message, ephemeral=True)

    @commands.hybrid_command(name="server", description="Get server stats")
    async def server(self, ctx: commands.Context):
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
    
    @commands.hybrid_command(name="info", description="Get server stats")
    async def info(self, ctx: commands.Context, member: discord.Member):
        """Get member stats."""
        
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
    async def avatar(self, ctx: commands.Context, member: commands.MemberConverter = None):
        """Fetch a user's avatar"""
        
        # If member is not provided, default to the author
        if member is None:
            member = ctx.author
        
        # Fetch the member's avatar
        member_avatar = member.avatar if member.avatar else member.default_avatar
        
        # Send the message
        await ctx.reply(f"↓ <@{member.id}>'s avatar ↓\n{member_avatar}")
    
    @commands.hybrid_command(name="indb", description="Check if the user is in the database, if so, provide the data.")
    async def avatar(self, ctx: commands.Context, member: commands.MemberConverter = None):
        user_id = member.id if member else ctx.author.id
        user = await ctx.bot.db.fetchrow('SELECT * FROM users WHERE user_id = $1', user_id)
        
        if user:
            db_user_id = user['user_id']
            db_translate_to = user['translate_to']
            await ctx.reply(f"user_id: {db_user_id}, translate_to: {db_translate_to}")
        else:
            await ctx.reply("User not in db.")

@bot.tree.context_menu(name='Show Info')
async def member_info_context_menu(interaction: discord.Interaction, user: discord.Member):
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

# SETUP
def setup(bot: commands.Bot):
    bot.add_cog(Info(bot))