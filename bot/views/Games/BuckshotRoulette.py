import time
import datetime
from enum import Enum
from random import randint, shuffle, choice
from asyncio import sleep, create_task

import discord

def ordinal(x):
    ordinals = [
        "first", "second", "third", "fourth", "fifth",
        "sixth", "seventh", "eighth", "ninth", "tenth",
        "eleventh", "twelfth"]
    return ordinals[x-1]

class Shell(Enum):
    BLANK = 0
    LIVE = 1


class Item(Enum):
    BEER = 0 #DONE
    # ADRENALINE = 1 #WILL NEED A VIEW OF ITS OWN
    INVERTER = 2 #DONE
    # JAMMER = 3 #WILL NEED GAME VIEW MODIFICATION

    MAGNIFYING_GLASS = 4 #DONE
    BURNER_PHONE = 5

    # HANDSAW = 6 #WILL NEED GAME VIEW MODIFICATION
    # HANDCUFFS = 7 #WILL NEED GAME VIEW MODIFICATION

    CIGARETTES = 8
    EXPIRED_MEDICINE = 9

    REMOTE = 10


class Shotgun:
    def __init__(self) -> None:
        self.sawed_off = False
    
    def load(self, blanks: int, lives: int):
        self.sawed_off = False
        self.__magazine = [Shell.LIVE for _ in range(lives)]
        self.__magazine.extend([Shell.BLANK for _ in range(blanks)])
        shuffle(self.__magazine)
    
    def discard_all_shells(self) -> None:
        self.sawed_off = False
        self.__magazine = []
    
    def shells_left(self) -> int:
        return len(self.__magazine)
    
    def fire(self) -> Shell:
        if self.shells_left() > 0:
            fired_round = self.__magazine.pop(0)
            self.sawed_off = False
            return fired_round
        
        raise Exception("Cannot fire.")
    
    def check_next_shell(self) -> Shell:
        return self.__magazine[0]
    
    def check_random_shell(self) -> tuple[Shell, int] | tuple[None, None]:
        shells_left = self.shells_left()
        if shells_left < 2:
            return None, None
        
        position = randint(1, shells_left-1)
        return self.__magazine[position], position+1
    
    def invert_current_shell(self) -> None:
        current_shell = self.__magazine[0]
        if current_shell == Shell.BLANK:
            self.__magazine[0] = Shell.LIVE
            return
        self.__magazine[0] = Shell.BLANK


class BuckshotRouletteView(discord.ui.View):

    def __init__(self, players: list[discord.Member], extreme: bool = False) -> None:
        super().__init__()
        self.players: list[discord.Member] = players
        self.current_player: int = 0
        self.players_ready: list[int] = []

        self.extreme = extreme


    async def setup_lobby_embed(self) -> discord.Embed:
        all_players_ids = [player.id for player in self.players]
        not_ready_players = all_players_ids
        for player_id in self.players_ready:
            not_ready_players.remove(player_id)

        embed: discord.Embed = discord.Embed(
            color=discord.Color.dark_gray(),
            title='Buckshot Roulette' if not self.extreme else 'BUCKSHOT ROULETTE (EXTREME)',
            description="Waiting for players...",
            timestamp=datetime.datetime.now(),
        )
        embed.add_field(name='Ready', value=" | ".join(['<@' + str(player_id) + '>' for player_id in self.players_ready]))
        embed.add_field(name='Not Ready', value=" | ".join(['<@' + str(player_id) + '>' for player_id in not_ready_players]))
        return embed

    async def setup_game(self, interaction: discord.Interaction) -> None:
        
        game_view = BuckshotRouletteGameView(self.players, self.extreme, interaction.channel)
        embed = await game_view.setup_game_embed()
        message = await interaction.channel.send(embed=embed, view=game_view)
        game_view.message = message
    
    @discord.ui.button(
        label='Ready',
        custom_id='button_ready',
        style=discord.ButtonStyle.success,
        row=0,
        emoji='✅'
    )
    async def button_ready_callback(self, interaction: discord.Interaction, button: discord.Button) -> None:
        if interaction.user.id not in [player.id for player in self.players]:
            return
        if interaction.user.id in self.players_ready:
            return
        
        await interaction.response.defer()

        self.players_ready.append(interaction.user.id)
        new_embed = await self.setup_lobby_embed()

        if len(self.players_ready) == len(self.players):
            await interaction.message.reply('all players are ready')
            button.disabled = True
            await self.setup_game(interaction)
            await interaction.message.delete()
            return

        await interaction.message.edit(embed=new_embed, view=self)


class PlayerSelect(discord.ui.Select):
    def __init__(self, players: list[tuple[str, int]], original_view: BuckshotRouletteGameView, shooter_id: int):
        options = [
            discord.SelectOption(label=player, value=player_id) for player, player_id in players
            ]
        super().__init__(placeholder="Who to shoot?", options=options)
        self.shooter_id = shooter_id
        self.original_view = original_view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.shooter_id:
            await interaction.response.send_message('Not your turn.', ephemeral=True)
            return
        
        await self.original_view.shoot_player(interaction.user.id, int(self.values[0]))
        await interaction.message.delete(delay=1)
        
class PlayerSelectView(discord.ui.View):
    def __init__(self, players: list[tuple[str, int]], original_view: BuckshotRouletteGameView, shooter_id: int):
        super().__init__()
        self.add_item(PlayerSelect(players, original_view, shooter_id))


class BuckshotRouletteGameView(discord.ui.View):

    def __init__(self, players: list[discord.Member], extreme: bool, channel: discord.TextChannel) -> None:
        super().__init__()
        self.players: list[discord.Member] = players
        self.rotation: str = 'forward'
        self.current_player: int = 0
        self.history: list[str] = []
        self.inventory: dict[int, list[Item]] = {}
        self.health_points: dict[int, int] = {}


        self.message: discord.Message = None
        self.channel: discord.TextChannel = channel
        
        self.base_hp = 1
        for i in range(len(self.players)):
            self.health_points[i] = self.base_hp

        self.shotgun = Shotgun()
        self.shells_live = randint(1, 4)
        self.shells_blank = randint(1, 4)
        self.shotgun.load(self.shells_blank, self.shells_live)
        self.extreme = extreme

        create_task(self.channel.send('GAME START', delete_after=10))
        create_task(self.channel.send(f"{self.shells_live} LIVE", delete_after=10))
        create_task(self.channel.send(f"{self.shells_blank} BLANK", delete_after=10))

        self.max_inventory_size: int = 8
        amount_of_items = 4
        available_items = list(Item)
        for i in range(len(self.players)):
            if not self.inventory.get(i):
                self.inventory[i] = []
            items_picked_up = []
            item_selection = [choice(available_items) for _ in range(amount_of_items)]
            for item in item_selection:
                if len(self.inventory[i]) == 8:
                    break
                self.inventory[i].append(item)
                items_picked_up.append(item)
            
            player_inventory_formatted_count = {}
            for item in items_picked_up:
                if player_inventory_formatted_count.get(item):
                    player_inventory_formatted_count[item] += 1
                    continue
                player_inventory_formatted_count[item] = 1
            player_inventory_formatted: list[tuple[str, int]] = []
            for item, count in player_inventory_formatted_count.items():
                player_inventory_formatted.append((f"{item.name} x{count}", item.value))
            
            string_formatted = f"{self.players[i].mention} PICKED UP\n"
            for item_string, item_id in player_inventory_formatted:
                string_formatted += item_string + ' '

            create_task(self.channel.send(string_formatted, delete_after=5))
    
    def reset_game(self) -> None:
        self.shells_live = randint(1, 4)
        self.shells_blank = randint(1, 4)
        self.shotgun.load(self.shells_blank, self.shells_live)

        amount_of_items = 4
        available_items = list(Item)
        for i in range(len(self.players)):
            if not self.inventory.get(i):
                self.inventory[i] = []
            items_picked_up = []
            item_selection = [choice(available_items) for _ in range(amount_of_items)]
            for item in item_selection:
                if len(self.inventory[i]) == 8:
                    break
                self.inventory[i].append(item)
                items_picked_up.append(item)
            
            player_inventory_formatted_count = {}
            for item in items_picked_up:
                if player_inventory_formatted_count.get(item):
                    player_inventory_formatted_count[item] += 1
                    continue
                player_inventory_formatted_count[item] = 1
            player_inventory_formatted: list[tuple[str, int]] = []
            for item, count in player_inventory_formatted_count.items():
                player_inventory_formatted.append((f"{item.name} x{count}", item.value))
            
            string_formatted = f"{self.players[i].mention} PICKED UP\n"
            for item_string, item_id in player_inventory_formatted:
                string_formatted += item_string + ' '

            create_task(self.channel.send(string_formatted, delete_after=5))
    
    def set_next_player(self) -> None:
        amount_of_players = len(self.players)
        complete = False
        current_position = self.current_player
        initial_position = self.current_player
        if self.rotation == 'forward':
            while not complete:
                current_position = self.rotate_forward_number(current_position)
                if self.health_points[current_position] > 0:
                    complete = True
                elif initial_position == current_position:
                    return
        elif self.rotation == 'backwards':
            while not complete:
                current_position = self.rotate_backwards_number(current_position)
                if self.health_points[current_position] > 0:
                    complete = True
                elif initial_position == current_position:
                    return
        self.history = []
        self.current_player = current_position
        create_task(self.channel.send(f'{self.players[self.current_player].mention} NOW HAS THE GUN.', delete_after=10))
    
    def rotate_forward_number(self, current_position):
        if current_position == len(self.players)-1:
            return 0
        else:
            return current_position + 1
    
    def rotate_backwards_number(self, current_position):
        if current_position == 0:
            return len(self.players)-1
        else:
            return current_position - 1
        
    def get_current_player_id(self) -> int:
        return self.players[self.current_player].id

    def get_player_id_by_position(self, position: int) -> int:
        return self.players[position].id
    
    def get_player_position_by_id(self, player_id: int) -> int:
        players_ids = [player.id for player in self.players]
        return players_ids.index(player_id)

    def know_next_player(self) -> int | tuple[int, bool]:
        
        amount_of_players: int = len(self.players)
        current_position: int = self.current_player
        initial_position: int = self.current_player
        eligible_players: list[int] = []

        for player, health in self.health_points.items():
            if health > 0:
                eligible_players.append(player)
        
        if len(eligible_players) == 1:
            if self.rotation == 'forward':
                while True:
                    if self.health_points[current_position] > 0:
                        break
                    current_position = self.rotate_forward_number(current_position)
                    if initial_position == current_position:
                        print('looping')
            elif self.rotation == 'backwards':
                while True:
                    if self.health_points[current_position] > 0:
                        break
                    current_position = self.rotate_backwards_number(current_position)
                    if initial_position == current_position:
                        print('looping')
            
            return (current_position, True)

        if self.rotation == 'forward':
            while True:
                current_position = self.rotate_forward_number(current_position)
                if self.health_points[current_position] > 0:
                    break
                if initial_position == current_position:
                    raise Exception('zero players left')
        elif self.rotation == 'backwards':
            while True:
                current_position = self.rotate_backwards_number(current_position)
                if self.health_points[current_position] > 0:
                    break
                if initial_position == current_position:
                    raise Exception('Zero players left')
        
        return current_position, False

    async def shoot_player(self, player_id: int, target_id: int):
        players_ids = [player.id for player in self.players]
        player_position = players_ids.index(player_id)
        target_position = players_ids.index(target_id)
        target: discord.Member = self.players[target_position]
        player: discord.Member = self.players[player_position]

        sawed_off = self.shotgun.sawed_off
        shell: Shell = self.shotgun.fire()
        if shell == Shell.LIVE:
            if not sawed_off:
                self.health_points[target_position] -= 1
            else:
                if self.health_points[target_position] >= 3:
                    self.health_points[target_position] -= 2
                else:
                    self.health_points[target_position] = 0
            self.set_next_player()
        if shell == Shell.BLANK:
            if player_id != target_id:
                self.set_next_player()

        await self.message.channel.send(f'{player.mention} SHOT {target.mention} WITH A {shell.name}', delete_after=10.0)
        new_embed = await self.setup_game_embed()
        if self.health_points[target_position] == 0:
            await self.message.channel.send(f'{self.players[target_position].mention} IS OUT...', delete_after=10.0)
            if self.extreme:
                await self.punish_player(target_position)
        await self.message.edit(view=self, embed=new_embed)
    
    async def punish_player(self, player_position: int):
        try:
            await self.players[player_position].timeout(datetime.timedelta(seconds=10))
        except:
            await self.channel.send(f"COULDN'T PUNISH {self.players[player_position]}...")

    async def setup_game_embed(self, embed_to_update: discord.Embed = None) -> discord.Embed:
        next_up, one_player_left = self.know_next_player()

        if one_player_left:
            name_list = [member.mention + f"⚡x{self.health_points[self.get_player_position_by_id(member.id)]}" for member in self.players]
            embed: discord.Embed = discord.Embed(
                color=discord.Color.red() if not self.extreme else discord.Color.dark_gray(),
                title='Buckshot Roulette' if not self.extreme else 'BUCKSHOT ROULETTE (EXTREME)',
                description="\n".join(name_list),
                timestamp=datetime.datetime.now(),
            )
            embed.add_field(name='Won the game', value=self.players[next_up].mention)
            for child in self.children:
                child.disabled = True
            await self.channel.send(f"{self.players[next_up].mention} WON", delete_after=10)
            
            return embed
            
            
        
        if self.shotgun.shells_left() == 0:
            self.reset_game()
            await self.channel.send('NEW ROUND', delete_after=10)
            await self.channel.send(f"{self.shells_live} LIVE", delete_after=10)
            await self.channel.send(f"{self.shells_blank} BLANK", delete_after=10)
            embed_to_update = None
        
        if embed_to_update is None:
            name_list = [member.mention + f"⚡x{self.health_points[self.get_player_position_by_id(member.id)]}" for member in self.players]
            embed: discord.Embed = discord.Embed(
                color=discord.Color.red() if not self.extreme else discord.Color.dark_gray(),
                title='Buckshot Roulette' if not self.extreme else 'BUCKSHOT ROULETTE (EXTREME)',
                description="\n".join(name_list),
                timestamp=datetime.datetime.now(),
            )
            embed.add_field(name='Holding the shotgun:', value=self.players[self.current_player].mention + f'⚡x{self.health_points[self.current_player]}')
            embed.add_field(name='Actions taken:', value='\n'.join(self.history))
            embed.add_field(name='Next up:', value=self.players[next_up].mention + f'⚡x{self.health_points[next_up]}')
            embed.set_footer(text=f"Direction: {self.rotation}")
            return embed
        
        embed_to_update.set_field_at(1, name='Actions taken:', value=' | '.join(self.history))
        embed_to_update.set_field_at(0, name='Holding the shotgun:', value=self.players[self.current_player].mention + f'⚡x{self.health_points[self.current_player]}')
        embed_to_update.set_field_at(2, name='Next up:', value=self.players[next_up].mention + f'⚡x{self.health_points[next_up]}')
        return embed_to_update

    
    @discord.ui.button(
        label='Shoot',
        custom_id='button_shoot',
        style=discord.ButtonStyle.primary,
        row=0, 
    )
    async def button_shoot_callback(self, interaction: discord.Interaction, button: discord.Button) -> None:
        if interaction.user.id != self.players[self.current_player].id:
            await interaction.response.send_message('Not your turn.', ephemeral=True)
            return
        eligible_players: list[int] = []

        for player, health in self.health_points.items():
            if health > 0:
                eligible_players.append(player)
        eligible_players.remove(self.current_player)

        eligible_players_data = [(self.players[player].display_name, self.players[player].id) for player in eligible_players]
        eligible_players_data.insert(0, ('Yourself', interaction.user.id))

        await interaction.response.send_message(view=PlayerSelectView(eligible_players_data, self, interaction.user.id), delete_after=15)


    @discord.ui.button(
        label='Use item',
        custom_id='button_use_item',
        style=discord.ButtonStyle.primary,
        row=0,
    )
    async def button_use_item_callback(self, interaction: discord.Interaction, button: discord.Button) -> None:
        if interaction.user.id != self.players[self.current_player].id:
            await interaction.response.send_message('Not your turn.', ephemeral=True)
            return
        
        player_inventory: list[Item] = self.inventory[self.current_player]
        if not player_inventory:
            await interaction.response.send_message('No items left', ephemeral=True)
            return
        view = InventoryView(self)
        await interaction.response.send_message(view=view, delete_after=15)


    @discord.ui.button(
        label='View Inventory',
        custom_id='button_view_inventory',
        style=discord.ButtonStyle.secondary,
        row=0,
        emoji='🔍'
    )
    async def button_view_inventory_callback(self, interaction: discord.Interaction, button: discord.Button) -> None:
        view = InventoryViewView(self)
        await interaction.response.send_message(view=view, ephemeral=True)
        

class InventorySelect(discord.ui.Select):
    def __init__(self, original_view: BuckshotRouletteGameView):
        player_inventory: list[Item] = original_view.inventory[original_view.current_player]
        player_inventory_formatted_count = {}
        for item in player_inventory:
            if player_inventory_formatted_count.get(item):
                player_inventory_formatted_count[item] += 1
                continue
            player_inventory_formatted_count[item] = 1
        player_inventory_formatted: list[tuple[str, int]] = []
        for item, count in player_inventory_formatted_count.items():
            player_inventory_formatted.append((f"{item.name} x{count}", item.value))

        options = [
            discord.SelectOption(label=item_name, value=item_value) for item_name, item_value in player_inventory_formatted
            ]
        super().__init__(placeholder="Choose an item", options=options)
        self.original_view = original_view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.original_view.players[self.original_view.current_player].id:
            await interaction.response.send_message('Not your turn.', ephemeral=True)
            return
        
        player_inventory: list[Item] = self.original_view.inventory[self.original_view.current_player].copy()
        player_inventory.remove(Item(int(self.values[0])))
        self.original_view.inventory[self.original_view.current_player] = player_inventory
        
        await self.original_view.channel.send(f"{interaction.user.mention} USED {Item(int(self.values[0])).name}", delete_after=10)

        if Item(int(self.values[0])) == Item.MAGNIFYING_GLASS:
            await interaction.response.send_message(f'{self.original_view.shotgun.check_next_shell().name}...', ephemeral=True)

        elif Item(int(self.values[0])) == Item.BEER:
            ejected_shell = self.original_view.shotgun.fire()
            await interaction.response.send_message(f'RACKED THE SHOTGUN... {ejected_shell.name}...', delete_after=10)

        elif Item(int(self.values[0])) == Item.CIGARETTES:
            current_health = self.original_view.health_points[self.original_view.current_player]
            if current_health == self.original_view.base_hp:
                pass
            else:
                self.original_view.health_points[self.original_view.current_player] += 1
                await interaction.response.send_message(f'RESTORED 1 HEALTH', delete_after=10)
        
        elif Item(int(self.values[0])) == Item.EXPIRED_MEDICINE:
            medicine_worked = bool(randint(0, 1))
            medicine_string = ''
            current_health = self.original_view.health_points[self.original_view.current_player]

            if not medicine_worked:
                medicine_string += 'BAD MEDICINE. '
                if current_health >= 1:
                    self.original_view.health_points[self.original_view.current_player] -= 1
                    medicine_string += 'LOST 1 HEALTH POINT.'
                else:
                    self.original_view.health_points[self.original_view.current_player] = 0
                    await interaction.response.send_message(f"{self.original_view.players[self.original_view.current_player].mention} IS OUT...")
                    if self.original_view.extreme:
                        await self.original_view.punish_player(self.original_view.current_player)
                
            else:
                medicine_string += 'GOOD MEDICINE. '
                if current_health <= self.original_view.base_hp-2:
                    self.original_view.health_points[self.original_view.current_player] += 2
                    medicine_string += 'RESTORED 2 HEALTH POINTS'
                else:
                    self.original_view.health_points[self.original_view.current_player] = self.original_view.base_hp
                    medicine_string += 'RESTORED 1 HEALTH POINT.'
            await interaction.response.send_message(medicine_string, delete_after=10)

        elif Item(int(self.values[0])) == Item.INVERTER:
            self.original_view.shotgun.invert_current_shell()
        
        elif Item(int(self.values[0])) == Item.BURNER_PHONE:
            shell, position = self.original_view.shotgun.check_random_shell()
            if not shell and not position:
                await interaction.response.send_message(f'HOW UNFORTUNATE...', ephemeral=True)
            
            await interaction.response.send_message(f'{ordinal(position).upper()} SHELL... {shell.name.upper()}...', ephemeral=True)
        
        elif Item(int(self.values[0])) == Item.REMOTE:
            self.original_view.rotation = 'backwards' if self.original_view.rotation == 'forward' else 'forward'
            await interaction.response.send_message(f'NOW WE GO {self.original_view.rotation.upper()}', delete_after=10)


        embed = await self.original_view.setup_game_embed()
        await self.original_view.message.edit(embed=embed)
        await interaction.message.delete()

class InventoryView(discord.ui.View):
    def __init__(self, original_view) -> None:
        super().__init__()
        self.add_item(InventorySelect(original_view))



class InventoryViewSelect(discord.ui.Select):
    def __init__(self, original_view: BuckshotRouletteGameView):
        options = [
            discord.SelectOption(label=player.display_name, value=player.id) for player in original_view.players
            ]
        super().__init__(placeholder="Check Inventory", options=options)
        self.original_view = original_view
    
    async def callback(self, interaction: discord.Interaction):
        player_inventory: list[Item] = self.original_view.inventory[self.original_view.get_player_position_by_id(int(self.values[0]))]
        player_inventory_formatted_count = {}
        for item in player_inventory:
            if player_inventory_formatted_count.get(item):
                player_inventory_formatted_count[item] += 1
                continue
            player_inventory_formatted_count[item] = 1
        player_inventory_formatted: list[tuple[str, int]] = []
        for item, count in player_inventory_formatted_count.items():
            player_inventory_formatted.append((f"{item.name} x{count}", item.value))
        
        string_formatted = f"{self.original_view.players[self.original_view.get_player_position_by_id(int(self.values[0]))].display_name}'s Inventory\n"
        for item_string, item_id in player_inventory_formatted:
            string_formatted += item_string + ' '
        
        await interaction.response.send_message(string_formatted, ephemeral=True)

class InventoryViewView(discord.ui.View):
    def __init__(self, original_view) -> None:
        super().__init__()
        self.add_item(InventoryViewSelect(original_view))
