import discord
from discord.ext import commands
import asyncio

from core.bot import logger, EngineerBot
from . import acceptable_errors

class Ranking(commands.Cog):
    needs_api = True

    def __init__(self, bot: EngineerBot) -> None:
        self.bot: EngineerBot = bot

    @commands.hybrid_command(name="rank", description="Check your rank.")
    async def rank(self, ctx: commands.Context) -> None:
        async with self.bot.session.get(
                '/api/guild_members/', 
                params = {
                    'user__id': ctx.author.id, 
                    'guild__id': ctx.guild.id
                },
                ) as response:
            json_response = await response.json()
        
        if response.status == 404 or not json_response:
            async with self.bot.session.post(
                    f"/api/users/", 
                    data = {
                        'id': ctx.author.id,
                    },
                ) as response:
                pass
            async with self.bot.session.post(
                    f"/api/guilds/", 
                    data = {
                        'id': ctx.guild.id,
                    },
                ) as response:
                pass
            async with self.bot.session.post(
                    "/api/guild_members/",
                    data = {
                        "user": f"{self.bot.session._base_url}/api/users/{ctx.author.id}/",
                        "guild": f"{self.bot.session._base_url}/api/guilds/{ctx.guild.id}/",
                    },
                ) as response:
                pass
            async with self.bot.session.get(
                '/api/guild_members/', 
                params = {
                    'user__id': ctx.author.id, 
                    'guild__id': ctx.guild.id
                },
                ) as response:
                json_response = await response.json()
        
        json_data = json_response[0] if response and response.status == 200 else None
            
        await ctx.reply(json_data['chat_experience'])
        

    async def cog_command_error(self, ctx: commands.Context, error: Exception) -> None:
        await ctx.message.add_reaction('❌')
        await ctx.send_help(ctx.command)

        if type(error) not in acceptable_errors:
            logger.error("Error in cog %s.", self.qualified_name, exc_info=error)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id:
            return
        
        if message.clean_content.startswith(str(self.bot.command_prefix)):
            return
        
        async with self.bot.session.get(
                '/api/guild_members/', 
                params = {
                    'user__id': message.author.id, 
                    'guild__id': message.guild.id
                },
                ) as response:
            json_response = await response.json()
        
        if response.status == 404 or not json_response:
            async with self.bot.session.post(
                    f"/api/users/", 
                    data = {
                        'id': message.author.id,
                    },
                ) as response:
                pass
            async with self.bot.session.post(
                    f"/api/guilds/", 
                    data = {
                        'id': message.guild.id,
                    },
                ) as response:
                pass
            async with self.bot.session.post(
                    "/api/guild_members/",
                    data = {
                        "user": f"{self.bot.session._base_url}/api/users/{message.author.id}/",
                        "guild": f"{self.bot.session._base_url}/api/guilds/{message.guild.id}/",
                    },
                ) as response:
                pass
            async with self.bot.session.get(
                '/api/guild_members/', 
                params = {
                    'user__id': message.author.id, 
                    'guild__id': message.guild.id
                },
                ) as response:
                json_response = await response.json()
        
        json_data = json_response[0] if response and response.status == 200 else None

        async with self.bot.session.patch(
                json_data['url'], 
                data = {
                    'chat_experience': json_data['chat_experience'] + 2
                },
                ) as response:
            pass


async def setup(bot: commands.Bot) -> None:
    if Ranking.needs_api and not bot._api_enabled:
        raise commands.ExtensionError('This extension needs api enabled.')
    
    await bot.add_cog(Ranking(bot))
