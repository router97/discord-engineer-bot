from typing import Optional

from discord import Intents, Activity, ActivityType, Status
from discord.ext import commands

from .config import COMMAND_PREFIX
from .help_command import CustomHelpCommand


# intents = Intents.default()
# intents.members = True
# intents.message_content = True
# intents.presences = True
# intents.moderation = True
# intents.all = True


bot = commands.Bot(
    command_prefix=COMMAND_PREFIX,
    intents=Intents.all(),
    help_command=CustomHelpCommand(),
)


async def setup_activity(name: Optional[str] = '.help') -> None:
    if len(name) > 128:
        name: str = name[:125] + "..."

    activity = Activity(
        name=name,
        type=ActivityType.playing,
        # state=f'⚙️ Version {}',
        # url='https://discord.com/oauth2/authorize?client_id=1167747112465858580',
    )
    await bot.change_presence(activity=activity, status=Status.online)
