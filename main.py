import os
import json

import discord
from discord import app_commands

from views.rps_buttons import RPS_Buttons
from views.ttt_buttons import TTT_Buttons
from views.rr_buttons import RR_Buttons
from config import config
from bot import bot, translator


# CONTEXT MENUS
@bot.tree.context_menu(name='Rock, Paper, Scissors')
async def rps_context_menu(interaction: discord.Interaction, user: discord.Member):
    """Rock, Paper, Scissors context menu."""
    
    # You can't play with yourself
    if interaction.user == user:
        return await interaction.response.send_message('typen', ephemeral=True)
    
    # Making an embed
    embed = discord.Embed(title='Rock, Paper, Scissors')
    
    embed.add_field(name=interaction.user.display_name, value='Not Ready')
    embed.add_field(name=user.display_name, value='Not Ready')
        
    # Setting up the buttons
    buttons = RPS_Buttons(user1=interaction.user, user2=user)
    
    # Sending the message
    await interaction.response.send_message(view=buttons, embed=embed)

@bot.tree.context_menu(name='Tic, Tac, Toe')
async def ttt_context_menu(interaction: discord.Interaction, user: discord.Member):
    """Tic, Tac, Toe context menu."""
    
    # You can't play with yourself
    if interaction.user == user:
        return await interaction.response.send_message('typen', ephemeral=True)
    
    # Making an embed
    embed = discord.Embed(title='Tick, Tack, Toe', color=discord.Color.red())
    
    embed.add_field(name='Board', value=':white_large_square::white_large_square::white_large_square:\n'*3)
    embed.set_author(name=f"{interaction.user.display_name} vs {user.display_name}")
    
    # Setting up the buttons
    buttons = TTT_Buttons(user1=interaction.user, user2=user)
    
    # Sending the message
    await interaction.response.send_message(view=buttons, embed=embed)

@bot.tree.context_menu(name='Russian Roulette')
async def rr_context_menu(interaction: discord.Interaction, user: discord.Member):
    """Russian Roulette context menu."""
    
    # You can't play with yourself
    if interaction.user == user:
        return await interaction.response.send_message('typen застрелился не так работает', ephemeral=True)
    
    # Making an embed
    embed = discord.Embed(title='Russian Roulette')
    embed.add_field(name='Turn', value=interaction.user.display_name)
    embed.add_field(name='Barrel', value='⦿⦿⦿⦿⦿⦿')
    embed.set_author(name=f"{interaction.user.display_name} vs {user.display_name}")
    
    # Setting up the buttons
    buttons = RR_Buttons(user1=interaction.user, user2=user)
    
    # Sending the message
    await interaction.response.send_message(view=buttons, embed=embed)

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

async def translate_message_callback(interaction: discord.Interaction, message: discord.Message):
    file_path = "data/users.json"
    
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, "r", encoding="utf-8") as fl:
            all_dict = json.load(fl)
    else:
        all_dict = {}
    
    user_key = str(interaction.user.id)
        
    if user_key not in all_dict:
        all_dict[user_key] = {}
    
    language_code = all_dict[user_key].get('lang', 'en')
    
    embed = discord.Embed(color=discord.Color.red(), description=translator.translate(message.content, dest=language_code).text)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

translate_context_menu = app_commands.ContextMenu(
    name='Translate',
    callback=translate_message_callback,
)
bot.tree.add_command(translate_context_menu)

# FUNCTIONS
async def setup_cogs():
    from cogs.Fun import Fun
    # from cogs.Moderation import Moderation
    from cogs.Games import Games
    from cogs.Info import Info
    from cogs.Translation import Translation
    
    await bot.add_cog(Fun(bot))
    # await bot.add_cog(Moderation(bot))
    await bot.add_cog(Games(bot))
    await bot.add_cog(Info(bot))
    await bot.add_cog(Translation(bot))
    await bot.tree.sync()


# EVENTS
@bot.event
async def on_ready():
    await setup_cogs()
    print(f"Logged in as {bot.user.name} ({bot.user.id})")


# LAUNCH
if __name__ == '__main__':
    bot.run(config['token'])