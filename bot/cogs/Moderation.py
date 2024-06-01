import discord
from discord.ext import commands


class Moderation(commands.Cog):
    """Moderation commands"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.hybrid_command(name="ban", description="Ban a member (permanently)")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: commands.MemberConverter, reason: str = 'No reason given'):
        """Ban a member (permanently)"""
        
        await ctx.guild.ban(member, reason=reason)
    
    @commands.hybrid_command(name="kick", description="Kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: commands.MemberConverter, reason: str ='No reason given'):
        """Kick"""
        
        # Kick the member
        await member.kick(reason=reason)
        
        # Sending a message
        await ctx.reply(f'kicked {member.mention} for "{reason}"')
    
    @kick.error
    async def kick_error(self, ctx: commands.Context, error: commands.CommandError):
        """Kick errors handler"""
        
        # Missing permissions handler
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("you are missing kick permissions", ephemeral=True)


def setup(bot):
    bot.add_cog(Moderation(bot))