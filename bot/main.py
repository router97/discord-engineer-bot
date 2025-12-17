from core.bot import bot
import core.config as config

def main() -> None:
    bot.run(config.DISCORD_BOT_TOKEN)

if __name__ == '__main__':
    main()
