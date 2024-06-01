"""
Utilities
=========

This cog module contains server utilities that are sometimes useful, 
like picking a random number or a random user from the guild.
"""

import datetime
from random import randint, choice

import discord
from discord.ext import commands


class Utilities(commands.Cog):
    """Miscellaneous commands"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.hybrid_command(name="rand", description="Generate a random number")
    async def rand(self, ctx: commands.Context, 
                   fro: str = commands.parameter(
                       default='0', 
                       description='From this number', 
                       displayed_default='0', 
                       displayed_name='From'
                   ), 
                   to: str = commands.parameter(
                       default='100', 
                       description='To this number', 
                       displayed_default='100', 
                       displayed_name='To'
                    )):
        
        """Generate a random number."""
        
        # Check if given arguments are valid integers
        try:
            start, finish = int(fro), int(to)
        except ValueError:
            return await ctx.reply("Not a valid number.")
        
        # Check if start is equal to finish or the same
        if start == finish or start > finish:
            return await ctx.reply("Not a valid range.")
        
        await ctx.reply(f"{randint(start, finish)}")
    
    @commands.hybrid_command(name="randmember", description="Ping a random member from the guild.")
    async def randmember(self, ctx: commands.Context):
        """Ping a random member from the guild"""
        
        # Get a list of server members without bots
        real_members_mentions = [member.mention for member in ctx.guild.members if not member.bot]
        
        # Send a random member from the list
        await ctx.reply(f"{choice(real_members_mentions)}")
    
    @commands.hybrid_command(name="listroles", description="List roles and their members.")
    async def listroles(self, ctx: commands.Context, title: str, *, role_names: str):
        
        role_names_list = [role_name.strip() for role_name in role_names.split()]
        roles: list[discord.Role] = []
        for role_name in role_names_list:
            role = await commands.RoleConverter().convert(ctx, role_name)
            if role:
                roles.append(role)
            else:
                await ctx.message.add_reaction(u'\u274c')
                await ctx.reply(f"Role `{role_name}` not found.")
                return
        
        embed = discord.Embed(
            color=discord.Color.teal(), 
            title=title, 
            timestamp=datetime.datetime.now(), 
        )
        embed.set_thumbnail(url=ctx.guild.icon.url)
        
        for role in roles:
            embed.add_field(name=role.name, value='\n'.join(f'- {member.mention}' for member in role.members) if role.members else '-', inline=False)
    
        await ctx.send(embed=embed, silent=True, allowed_mentions=discord.AllowedMentions.none())
        await ctx.message.delete()


# SETUP
def setup(bot: commands.Bot):
    bot.add_cog(Utilities(bot))