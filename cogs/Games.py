import discord
from discord.ext import commands
 
from views.rps_buttons import RPS_Buttons
from views.ttt_buttons import TTT_Buttons
from views.rr_buttons import RR_Buttons


class Games(commands.Cog):
    """Games description."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.hybrid_command(name="ttt", description="Tic, Tac, Toe")
    async def ttt(self, ctx: commands.Context, member: commands.MemberConverter = commands.parameter(description="The member you want to play with")):
        """Tic, Tac, Toe"""
        
        # You can't play with yourself
        if ctx.author == member:
            return await ctx.reply('typen в крестики нолики сигма сам с собой поиграть хотел, проиграешь, даже не пытайся')
        
        # Making an embed
        embed = discord.Embed(title='Tick, Tack, Toe', color=discord.Color.red())
        embed.set_author(name=f"{ctx.author.display_name} vs {member.display_name}")
        embed.add_field(name='Board', value=':white_large_square::white_large_square::white_large_square:\n'*3)
        
        # Setting up the buttons
        buttons = TTT_Buttons(user1=ctx.author, user2=member)
        
        # Sending the message
        await ctx.reply(view=buttons, embed=embed)
    
    @commands.hybrid_command(name="rps", description="Rock, Paper, Scissors")
    async def rps(self, ctx: commands.Context, member: commands.MemberConverter = commands.parameter(description="The member you want to play with")):
        """Rock, Paper, Scissors"""
        
        # You can't play with yourself
        if ctx.author == member:
            return await ctx.reply('typen')
        
        # Making an embed
        embed = discord.Embed(title='Rock, Paper, Scissors', color=discord.Color.red())
        embed.add_field(name=ctx.author.display_name, value='Not Ready')
        embed.add_field(name=member.display_name, value='Not Ready')
        
        # Setting up the buttons
        buttons = RPS_Buttons(user1=ctx.author, user2=member)
        
        # Sending the message
        await ctx.reply(view=buttons, embed=embed)

    @commands.hybrid_command(name="rr", description="Russian Roulette")
    async def rr(self, ctx: commands.Context, member: commands.MemberConverter = commands.parameter(description="The member you want to play with")):
        """Russian Roulette"""
        
        # You can't play with yourself
        if ctx.author == member:
            return await ctx.reply('typen застрелился не так работает')
        
        # Making an embed
        embed = discord.Embed(title='Russian Roulette', color=discord.Color.red())
        embed.set_author(name=f"{ctx.author.display_name} vs {member.display_name}")
        embed.add_field(name='Turn', value=ctx.author.display_name)
        embed.add_field(name='Barrel', value='⦿⦿⦿⦿⦿⦿')
        
        # Setting up the buttons
        buttons = RR_Buttons(user1=ctx.author, user2=member)
        
        # Sending the message
        await ctx.reply(view=buttons, embed=embed)


# SETUP
def setup(bot: commands.Bot):
    bot.add_cog(Games(bot))