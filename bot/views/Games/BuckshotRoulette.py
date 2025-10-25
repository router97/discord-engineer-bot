import datetime
from enum import Enum
from random import randint, shuffle, choice
from asyncio import create_task
import asyncio

import discord


def ordinal(x: int) -> str:
    ordinals = [
        "first", "second", "third", "fourth", "fifth",
        "sixth", "seventh", "eighth", "ninth", "tenth",
        "eleventh", "twelfth"
        ]
    return ordinals[x-1]


class Shell(Enum):
    BLANK = 0
    LIVE = 1


class Item(Enum):
    BEER = 0
    ADRENALINE = 1
    INVERTER = 2

    MAGNIFYING_GLASS = 4
    BURNER_PHONE = 5

    HANDSAW = 6 
    HANDCUFFS = 7

    CIGARETTES = 8
    EXPIRED_MEDICINE = 9

    REMOTE = 10


class Shotgun:
    def __init__(self) -> None:
        self.sawed_off: bool = False
        self.__magazine: list[Shell] = []
    
    def load(self, blanks: int, lives: int) -> None:
        self.sawed_off = False
        self.__magazine = [Shell.LIVE for _ in range(lives)]
        self.__magazine.extend([Shell.BLANK for _ in range(blanks)])
        shuffle(self.__magazine)
    
    def discard_all_shells(self) -> None:
        self.sawed_off = False
        self.__magazine = []
    
    def fire(self) -> Shell:
        if not self.check_shells_left() > 0:
            raise Exception("Can't fire shotgun. No shells left")
    
        fired_round: Shell = self.__magazine.pop(0)
        self.sawed_off = False
        return fired_round

    def check_shells_left(self) -> int:
        return len(self.__magazine)
    
    def check_next_shell(self) -> Shell:
        return self.__magazine[0]
    
    def check_random_shell(self) -> tuple[Shell, int] | tuple[None, None]:
        shells_left = self.check_shells_left()

        if shells_left < 2:
            return None, None
        
        position = randint(1, shells_left - 1)
        return self.__magazine[position], position+1
    
    def invert_current_shell(self) -> None:
        self.__magazine[0] = Shell.BLANK if self.__magazine[0] == Shell.LIVE else Shell.LIVE


class BuckshotRouletteLobbyView(discord.ui.View):
    GENERAL_RELEASE_OF_LIABILITY_TEMPLATE: str = """This General Release ("Release") is made on {day} day of {month}, {year} between ████████ at ████████████████████████████████ ("Releasor") and ████████ at ████████████████████████ ("Releasee").

1. Releasor and anyone claiming on Releasor's behalf releases and forever discharges Releasee and its affiliates, successors, officers, employees, representatives, partners, agents and anyone claiming through them (collectively, the “Released Parties”), in their individual and/or corporate capacities from any and all claims, liabilities, obligations, promises, agreements, disputes, demands, damages, causes of action of any nature and kind, known or unknown, which Releasor has or ever had or may in the future have against Releasee or any of the Released Parties arising out of or relating to: the termination of a contractual relationship between the Releasor and the Releasee (“Claims”).

2. In exchange for the release of Claims, Releasee will provide Releasor a payment in the amount of $00,000.00. In consideration of such payment, Releasor agrees to accept the payment as full and complete settlement and satisfaction of any present and prospective claims.

3. This Release shall not be in any way construed as an admission by the Releasee that it has acted wrongfully with respect to Releasor or any other person, that it admits liability or responsibility at any time for any purpose, or that Releasor has any rights whatsoever against the Releasee.

4. This Release shall be binding upon the parties and their respective heirs, administrators, personal representatives, executors, successors and assigns. Releasor has the authority to release the Claims and has not assigned or transferred any Claims to any other party. The provisions of this Release are severable. If any provision is held to be invalid or unenforceable, it shall not affect the validity or enforceability of any other provision. This Release constitutes the entire agreement between the parties and supersedes any and all prior oral or written agreements or understandings between the parties concerning the subject matter of this Release. This Release may not be altered, amended or modified, except by a written document signed by both parties. The terms of this Release shall be governed by and construed in accordance with the laws of the State of ████████.
"""
    DENY_PLAYER_MESSAGES: list[str] = [
        "You are not part of the contract. *breaks pen angrily*",
        "You are not part of the contract. *breaks pen aggressively*",
        "You are not part of the contract. *breaks pen very aggressively*",
        "You are not part of the contract. *eats pen hungrily*",
        "You are not part of the contract. *takes your pen gently*",
        "You are not part of the uh.. The contract or whatever *does nothing passively*",
        "You are not part of the contract. *[sample text]*",
        "You are not part of the contract. *throws up*",
        "You are not part of the contract. *shits yourself*",
        "You are not part of... Uhm... You can't sign this.. I think *remembers forgetfully*",
        "Don't even try. *glares at you glaringly*",
        "Nope.",
        "Nah.",
        "No way.",
        "Uh, no.",
        "Heck no.",
        "Allright sign here and... Hold up... Something's not right...",
        ]
    EMBED_TITLE = 'GENERAL RELEASE OF LIABILITY'
    EMBED_COLOR = discord.Color.light_gray()

    def __init__(self, message: discord.Message, players: list[discord.Member], extreme: bool = False) -> None:
        super().__init__()
        self.players = players
        self.extreme = extreme
        self.message = message

        self.no_more_players_event = asyncio.Event()
        self.player_queue = asyncio.Queue()
        self.__players_ready = []
        self.created_at = datetime.datetime.now()

        asyncio.create_task(
            self.message.edit(view = self, embed=self.__setup_embed())
        )
        self.workers = [
            asyncio.create_task(
                self.__update_message_worker(),
            ),
            asyncio.create_task(
                self.__start_game_worker()
                )
        ]

    def __setup_embed(self) -> discord.Embed:
        not_ready_players = [player for player in self.players if player.id not in self.__players_ready]
        
        embed = discord.Embed(
            color=self.EMBED_COLOR,
            title=self.EMBED_TITLE,
            description=self.GENERAL_RELEASE_OF_LIABILITY_TEMPLATE.format(
                day=self.created_at.day,
                month=self.created_at.strftime("%B"),
                year=self.created_at.year
                ),
            timestamp=self.created_at,
        )
        embed.add_field(name='Signed', value=" | ".join(['<@' + str(player_id) + '>' for player_id in self.__players_ready]))
        embed.add_field(name='Not Signed', value=" | ".join([player.mention for player in not_ready_players]))
        return embed

    async def __start_game_service(self) -> None:
        game_view = BuckshotRouletteGameView(self.players, self.extreme, self.message.channel)

        embed = await game_view.setup_embed()
        message = await self.message.channel.send(embed=embed, view=game_view)

        # TODO NO
        game_view.message = message

        await self.message.delete()
    
    async def __start_game_worker(self) -> None:
        await self.no_more_players_event.wait()
        await self.__start_game_service()

    def __game_start_checker(self) -> None:
        if len(self.players) == len(self.__players_ready):
            self.no_more_players_event.set()

    async def __update_message_worker(self) -> None:
        while not self.no_more_players_event.is_set():
            collected_players = []

            first_player_collected = await self.player_queue.get()
            collected_players.append(first_player_collected)

            while True:
                try:
                    collected_player = self.player_queue.get_nowait()
                    collected_players.append(collected_player)
                except asyncio.QueueEmpty:
                    break
            
            self.__players_ready.extend(collected_players)
            self.__players_ready = list(dict.fromkeys(self.__players_ready))

            new_embed = self.__setup_embed()
            await self.message.edit(embed=new_embed)

            self.__game_start_checker()
            for _ in range(len(collected_players)):
                self.player_queue.task_done()

    @discord.ui.button(
        label = 'Sign',
        custom_id = 'button_ready',
        style = discord.ButtonStyle.danger,
        emoji = '🖊️',
        row = 0
    )
    async def button_ready_callback(self, interaction: discord.Interaction, button: discord.Button) -> None:
        if interaction.user not in self.players:
            await interaction.response.send_message(choice(self.DENY_PLAYER_MESSAGES), ephemeral=True, delete_after=10)
            return
        
        await interaction.response.defer()
        await self.player_queue.put(interaction.user.id)


class BuckshotRouletteGameView(discord.ui.View):
    NOT_PLAYERS_TURN_MESSAGES: list[str] = ['Not your turn.',
                                            'Nope.',
                                            'Not yet.'
                                            ]
    LIVE_SHELL_CASING_TOP: str = '🟥'
    LIVE_SHELL_CASING_BOTTOM: str = '🟥'
    BLANK_SHELL_CASING_TOP: str = '⬜'
    BLANK_SHELL_CASING_BOTTOM: str = '⬜'
    SHELL_PRIMER: str = '🟨'
    EMPTY_SYMBOL: str = '⠀'

    def __init__(self, players: list[discord.Member], extreme: bool, channel: discord.TextChannel) -> None:
        super().__init__()
        self.players: list[discord.Member] = players
        self.rotation: str = 'forward'
        self.current_player: int = 0
        self.history: list[str] = []
        self.inventory: dict[int, list[Item]] = {}
        self.health_points: dict[int, int] = {}
        self.skipping_turn: dict[int, bool] = {}
        self.handcuff_delay: dict[int, int] = {}
        self.message = None

        self.channel: discord.TextChannel = channel
        
        self.base_hp = 4
        for i in range(len(self.players)):
            self.health_points[i] = self.base_hp

        self.shotgun = Shotgun()
        self.shells_live = randint(1, 4)
        self.shells_blank = randint(1, 4)
        self.shotgun.load(self.shells_blank, self.shells_live)
        self.extreme = extreme

        shell_text = self.generate_shells_text()
        embed = discord.Embed(
            description=shell_text
        )
        create_task(self.channel.send(embed=embed, delete_after=10))
        

        self.max_inventory_size: int = 8
        amount_of_items = 3
        available_items = list(Item)
        for i in range(len(self.players)):
            if not self.inventory.get(i):
                self.inventory[i] = []
            items_picked_up = []
            item_selection = [choice(available_items) for _ in range(amount_of_items)]
            for item in item_selection:
                if len(self.inventory[i]) == self.max_inventory_size:
                    break
                self.inventory[i].append(item)
                items_picked_up.append(item)
    
    def generate_shells_text(self):
        first_line = ((self.LIVE_SHELL_CASING_TOP + self.EMPTY_SYMBOL) * self.shells_live) + ((self.BLANK_SHELL_CASING_TOP + self.EMPTY_SYMBOL) * self.shells_blank)
        second_line = ((self.LIVE_SHELL_CASING_BOTTOM + self.EMPTY_SYMBOL) * self.shells_live) + ((self.BLANK_SHELL_CASING_BOTTOM + self.EMPTY_SYMBOL) * self.shells_blank)
        last_line = (self.SHELL_PRIMER + self.EMPTY_SYMBOL) * (self.shells_blank + self.shells_live)
        return f'{first_line}\n{second_line}\n{last_line}'

    def reset_game(self) -> None:
        self.shells_live = randint(1, 4)
        self.shells_blank = randint(1, 4)
        shell_text = self.generate_shells_text()
        embed = discord.Embed(
            description=shell_text
        )
        create_task(self.channel.send(embed=embed, delete_after=10))
        self.shotgun.load(self.shells_blank, self.shells_live)

        amount_of_items = 3
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
    
    def know_next_player(self) -> tuple[int, bool]:
        
        amount_of_players: int = len(self.players)
        current_position: int = self.current_player
        initial_position: int = self.current_player
        eligible_players: list[int] = []
        complete = False

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
                        raise Exception("something's wrong with calculating who the next player is")
            elif self.rotation == 'backwards':
                while True:
                    if self.health_points[current_position] > 0:
                        break
                    current_position = self.rotate_backwards_number(current_position)
                    if initial_position == current_position:
                        raise Exception("something's wrong with calculating who the next player is")
            
            return (current_position, True)
        
        ignoring_positions = []
        if self.rotation == 'forward':
            while not complete:
                current_position = self.rotate_forward_number(current_position)
                if self.health_points[current_position] > 0 and current_position not in ignoring_positions:
                    if self.skipping_turn.get(current_position, False):
                        ignoring_positions.append(current_position)
                        continue
                    
                    complete = True
        elif self.rotation == 'backwards':
            while not complete:
                current_position = self.rotate_backwards_number(current_position)
                if self.health_points[current_position] > 0 and current_position not in ignoring_positions:
                    if self.skipping_turn.get(current_position, False):
                        ignoring_positions.append(current_position)
                        continue
                    complete = True
        
        return current_position, False

    def set_next_player(self) -> None:
        amount_of_players = len(self.players)
        for player in self.handcuff_delay.keys():
            if not self.handcuff_delay.get(player, 0):
                continue
            self.handcuff_delay[player] -= 1

        complete = False
        current_position = self.current_player
        initial_position = self.current_player
        ignoring_positions = []

        if self.rotation == 'forward':
            while not complete:
                current_position = self.rotate_forward_number(current_position)
                if self.health_points[current_position] > 0 and current_position not in ignoring_positions:
                    if self.skipping_turn.get(current_position, False):
                        ignoring_positions.append(current_position)
                        self.skipping_turn[current_position] = False
                        continue
                    complete = True
                    
        elif self.rotation == 'backwards':
            while not complete:
                current_position = self.rotate_backwards_number(current_position)
                if self.health_points[current_position] > 0 and current_position not in ignoring_positions:
                    if self.skipping_turn.get(current_position, False):
                        ignoring_positions.append(current_position)
                        self.skipping_turn[current_position] = False
                        continue
                    complete = True
        
        self.current_player = current_position
        create_task(self.channel.send(f'{self.players[self.current_player].mention} NOW HAS THE GUN.', delete_after=10))
    
    def rotate_forward_number(self, current_position: int) -> int:
        if current_position == len(self.players)-1:
            return 0
        else:
            return current_position + 1
    
    def rotate_backwards_number(self, current_position: int) -> int:
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

    async def shoot_player(self, player_id: int, target_id: int) -> None:
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
        elif shell == Shell.BLANK:
            if player_id != target_id:
                self.set_next_player()

        await self.channel.send(f'{player.mention} SHOT {target.mention} WITH A {shell.name}', delete_after=10.0)

        new_embed = await self.setup_embed()
        if self.health_points[target_position] == 0:
            await self.channel.send(f'{self.players[target_position].mention} IS OUT...', delete_after=10.0)
            if self.extreme:
                await self.punish_player(target_position)
        await self.message.edit(view=self, embed=new_embed)
    
    async def punish_player(self, player_position: int) -> None:
        try:
            await self.players[player_position].timeout(datetime.timedelta(seconds=10))
        except:
            await self.channel.send(f"COULDN'T PUNISH {self.players[player_position]}...", delete_after=20)

    async def setup_embed(self, embed_to_update: discord.Embed = None) -> discord.Embed:
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

            self.clear_items().stop()

            await self.channel.send(f"{self.players[next_up].mention} WON", delete_after=30)
            return embed
        
        if self.shotgun.check_shells_left() == 0:
            self.reset_game()
            embed_to_update = None
        
        if embed_to_update:
            embed_to_update.set_field_at(0, name='Holding the shotgun:', value=self.players[self.current_player].mention + f'⚡x{self.health_points[self.current_player]}')
            embed_to_update.set_field_at(1, name='Next up:', value=self.players[next_up].mention + f'⚡x{self.health_points[next_up]}')
            return embed_to_update
        name_list = [member.mention + f"⚡x{self.health_points[self.get_player_position_by_id(member.id)]}" for member in self.players]
        embed: discord.Embed = discord.Embed(
            color=discord.Color.red() if not self.extreme else discord.Color.dark_gray(),
            title='Buckshot Roulette' if not self.extreme else 'BUCKSHOT ROULETTE (EXTREME)',
            description="\n".join(name_list),
            timestamp=datetime.datetime.now(),
        )
        embed.add_field(name='Holding the shotgun:', value=self.players[self.current_player].mention + f'⚡x{self.health_points[self.current_player]}')
        embed.add_field(name='Next up:', value=self.players[next_up].mention + f'⚡x{self.health_points[next_up]}')
        embed.set_footer(text=f"Direction: {self.rotation}")
        return embed

    @discord.ui.button(
        label='Shoot',
        custom_id='button_shoot',
        style=discord.ButtonStyle.primary,
        row=0, 
    )
    async def button_shoot_callback(self, interaction: discord.Interaction, button: discord.Button) -> None:
        if interaction.user.id != self.players[self.current_player].id:
            await interaction.response.send_message(choice(self.NOT_PLAYERS_TURN_MESSAGES), ephemeral=True, delete_after=10)
            return
        
        eligible_players: list[int] = []

        for player, health in self.health_points.items():
            if health > 0:
                eligible_players.append(player)
        eligible_players.remove(self.current_player)

        eligible_players_data = [(self.players[player].display_name, self.players[player].id) for player in eligible_players]
        eligible_players_data.insert(0, ('Yourself', interaction.user.id))

        await interaction.response.send_message(view=ShootView(eligible_players_data, self, interaction.user.id), ephemeral=True, delete_after=20)

    @discord.ui.button(
        label='Use Item',
        custom_id='button_use_item',
        style=discord.ButtonStyle.primary,
        row=0,
    )
    async def button_use_item_callback(self, interaction: discord.Interaction, button: discord.Button) -> None:
        if interaction.user.id != self.players[self.current_player].id:
            await interaction.response.send_message(choice(self.NOT_PLAYERS_TURN_MESSAGES), ephemeral=True, delete_after=10)
            return
        
        player_inventory: list[Item] = self.inventory[self.current_player]

        if not player_inventory:
            await interaction.response.send_message('no items left(', ephemeral=True, delete_after=10)
            return
        
        view = UseItemView(self)
        await interaction.response.send_message(view=view, ephemeral=True, delete_after=20)

    @discord.ui.button(
        label='View Inventory',
        custom_id='button_view_inventory',
        style=discord.ButtonStyle.secondary,
        row=0,
        emoji='🔍'
    )
    async def button_view_inventory_callback(self, interaction: discord.Interaction, button: discord.Button) -> None:
        view = InventoryView(self)
        await interaction.response.send_message(view=view, ephemeral=True, delete_after=20)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not await super().interaction_check(interaction):
            return False

        if interaction.user not in self.players:
            return False
        
        return True


class ShootView(discord.ui.View):
    def __init__(self, players: list[tuple[str, int]], original_view: BuckshotRouletteGameView, shooter_id: int):
        super().__init__()
        self.add_item(ShootSelect(players, original_view, shooter_id))


class ShootSelect(discord.ui.Select):
    def __init__(self, players: list[tuple[str, int]], original_view: BuckshotRouletteGameView, shooter_id: int):
        options = [
            discord.SelectOption(label=player, value=player_id) for player, player_id in players
            ]
        super().__init__(placeholder="Who to shoot?", options=options)
        self.shooter_id = shooter_id
        self.original_view = original_view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.shooter_id:
            await interaction.response.send_message(choice(self.original_view.NOT_PLAYERS_TURN_MESSAGES), ephemeral=True, delete_after=10)
            return
        
        await interaction.response.defer(ephemeral=True)
        await self.original_view.shoot_player(interaction.user.id, int(self.values[0]))


class UseItemView(discord.ui.View):
    def __init__(self, original_view: BuckshotRouletteGameView) -> None:
        super().__init__()
        self.add_item(UseItemSelect(original_view))


class UseItemSelect(discord.ui.Select):
    LIVE_SHELL_IMAGE_URL = 'https://media.discordapp.net/attachments/1430510977840971786/1430511076751183923/latest.png?ex=68fa0ac2&is=68f8b942&hm=424717e30a469fe9376e390370b3c8d504960fc10cd6352bc3238ade6e44b3ff&=&format=webp&quality=lossless&width=731&height=731'
    BLANK_SHELL_IMAGE_URL = 'https://media.discordapp.net/attachments/1430510977840971786/1430511061131460719/latest.png?ex=68fa0abe&is=68f8b93e&hm=254ee2986c4666887a6f41dabbbafdc92d73dd756051abe2d60f36e017208bf1&=&format=webp&quality=lossless&width=731&height=731'

    def __init__(self, original_view: BuckshotRouletteGameView) -> None:
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
    
    async def callback(self, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.original_view.players[self.original_view.current_player].id:
            await interaction.response.send_message('Not your turn.', ephemeral=True)
            return
        
        player_inventory: list[Item] = self.original_view.inventory[self.original_view.current_player].copy()
        player_inventory.remove(Item(int(self.values[0])))
        self.original_view.inventory[self.original_view.current_player] = player_inventory
        
        await self.original_view.channel.send(f"{interaction.user.mention} USED {Item(int(self.values[0])).name}", delete_after=10)

        if Item(int(self.values[0])) == Item.MAGNIFYING_GLASS:
            next_shell = self.original_view.shotgun.check_next_shell()
            magnifying_glass_embed = discord.Embed(
                title=f'{next_shell.name}...',
                color=discord.Color.red() if next_shell == Shell.LIVE else discord.Color.light_gray(),
            ).set_image(url=self.BLANK_SHELL_IMAGE_URL if next_shell == Shell.BLANK else self.LIVE_SHELL_IMAGE_URL)
            
            await interaction.response.send_message(embed=magnifying_glass_embed, ephemeral=True)   

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
            else:
                await interaction.response.send_message(f'{ordinal(position).upper()} SHELL... {shell.name.upper()}...', ephemeral=True)
        
        elif Item(int(self.values[0])) == Item.REMOTE:
            self.original_view.rotation = 'backwards' if self.original_view.rotation == 'forward' else 'forward'
            await interaction.response.send_message(f'NOW WE GO {self.original_view.rotation.upper()}', delete_after=10)
        
        elif Item(int(self.values[0])) == Item.HANDSAW:
            self.original_view.shotgun.sawed_off = True

        elif Item(int(self.values[0])) == Item.HANDCUFFS:
            if self.original_view.handcuff_delay.get(self.original_view.current_player, 0):
                await interaction.response.send_message('CANNOT USE HANDCUFFS. (you lost them regardless)', delete_after=10, ephemeral=True)
            else:
                await interaction.response.send_message(view=HandcuffsView(self.original_view), delete_after=10, ephemeral=True)
                self.original_view.handcuff_delay[self.original_view.current_player] = 2
        
        elif Item(int(self.values[0])) == Item.ADRENALINE:
            await interaction.response.send_message(view=AdrenalineView(self.original_view), delete_after=10, ephemeral=True)

        embed = await self.original_view.setup_embed()
        await self.original_view.message.edit(embed=embed)
        # await interaction.message.delete()


class InventoryView(discord.ui.View):
    def __init__(self, original_view: BuckshotRouletteGameView) -> None:
        super().__init__()
        self.add_item(InventorySelect(original_view))


class InventorySelect(discord.ui.Select):
    def __init__(self, original_view: BuckshotRouletteGameView) -> None:
        options = [
            discord.SelectOption(label=player.display_name, value=player.id) for player in original_view.players
            ]
        super().__init__(placeholder="Check Inventory", options=options)
        self.original_view = original_view
    
    async def callback(self, interaction: discord.Interaction) -> None:
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


class HandcuffsView(discord.ui.View):
    def __init__(self, original_view: BuckshotRouletteGameView) -> None:
        super().__init__()
        self.add_item(HandcuffsSelect(original_view))


class HandcuffsSelect(discord.ui.Select):
    def __init__(self, original_view: BuckshotRouletteGameView) -> None:
        current_player_id = original_view.get_player_id_by_position(original_view.current_player)
        players_excluding_current = [player for player in original_view.players if player.id != current_player_id]
        options = [
            discord.SelectOption(label=player.display_name, value=original_view.get_player_position_by_id(int(player.id))) for player in players_excluding_current
            ]
        super().__init__(placeholder="Use handcuffs on", options=options)
        self.original_view = original_view

    async def callback(self, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.original_view.get_current_player_id():
            await interaction.response.send_message('Not your turn.', ephemeral=True)
            return
        
        await self.use(int(self.values[0]))
        await interaction.message.delete(delay=1)
    
    async def use(self, target_position: int) -> None:
        self.original_view.skipping_turn[target_position] = True
        await self.original_view.channel.send(f'USED HANDCUFFS ON {self.original_view.players[target_position].mention}.', delete_after=10)
        old_embed = self.original_view.message.embeds[0]
        new_embed = await self.original_view.setup_embed(old_embed)
        await self.original_view.message.edit(embed=new_embed)


class AdrenalineView(discord.ui.View):
    def __init__(self, original_view: BuckshotRouletteGameView) -> None:
        super().__init__()
        self.add_item(AdrenalineSelect(original_view))


class AdrenalineSelect(discord.ui.Select):
    def __init__(self, original_view: BuckshotRouletteGameView) -> None:
        available_inventories: dict[int, list[Item]] = {}
        for player in original_view.players:
            player_position = original_view.get_player_position_by_id(player.id)
            if not original_view.inventory.get(player_position, []):
                continue

            if player_position == original_view.current_player:
                continue
            
            if original_view.health_points[player_position] == 0:
                continue
            
            available_inventory = [item for item in original_view.inventory[player_position] if item != Item.ADRENALINE]
            if not available_inventory:
                continue
            available_inventories[player_position] = available_inventory

        available_inventories_formatted = []
        for player_position, inventory in available_inventories.items():
            owner_name = original_view.players[player_position].display_name
            player_inventory_formatted_count = {}
            for item in inventory:
                if player_inventory_formatted_count.get(item):
                    player_inventory_formatted_count[item] += 1
                    continue
                player_inventory_formatted_count[item] = 1

            for item, count in player_inventory_formatted_count.items():
                available_inventories_formatted.append((f"{owner_name} || {item.name} x{count}", f"{player_position}|{item.value}"))

        options = [
            discord.SelectOption(label=item_name, value=item_value) for item_name, item_value in available_inventories_formatted
            ]
        
        if not options:
            options = [discord.SelectOption(label='CONGRATS ON WASTING THE ITEM! nothing to steal', value='None')]
        
        super().__init__(placeholder="Steal an item", options=options)
        self.original_view = original_view 

    async def callback(self, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.original_view.get_current_player_id():
            await interaction.response.send_message('Not your turn.', ephemeral=True)
            return
        
        if self.values[0] == 'Nothing':
            await interaction.response.send_message("stole NOTHING from NO ONE", ephemeral=True, delete_after=10)
        await interaction.response.defer(ephemeral=True)


        owner_of_stolen_item_position = int(self.values[0].split("|")[0])
        used_item_id = int(self.values[0].split("|")[1])

        owner_inventory: list[Item] = self.original_view.inventory[owner_of_stolen_item_position].copy()
        owner_inventory.remove(Item(int(used_item_id)))
        self.original_view.inventory[owner_of_stolen_item_position] = owner_inventory

        player_inventory: list[Item] = self.original_view.inventory[self.original_view.current_player].copy()
        player_inventory.append(Item(int(used_item_id)))
        self.original_view.inventory[self.original_view.current_player] = player_inventory
        
        await self.original_view.channel.send(f"{interaction.user.mention} STOLE {Item(int(used_item_id)).name} FROM {self.original_view.players[owner_of_stolen_item_position].mention}.", delete_after=10)
