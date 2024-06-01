# discord-engineer-bot

It's a simple discord bot with features like: Games, Translation, Utilities

> [!IMPORTANT]
> These docs are unfinished.


# Commands
Commands of this bot.

[Games](#games)

[Translation](#translation)


## Games
This cog module contains some simple message-based games using message components like embeds and buttons.

| Command | Description                          | Has a context menu? |
|---------|--------------------------------------|---------------------|
| ttt     | A simple tic-tac-toe game.           | Yes.                |
| rps     | A simple rock, paper, scissors game. | Yes.                |
| rr      | A simple russian roulette game.      | Yes.                |


## Translation
This cog module contains commands that help with localization and translation.

| Command | Description                                  | Has a context menu? |
|---------|----------------------------------------------|---------------------|
| t       | Translate a message.                         | Yes.                |
| setlang | Set your preferred language for translation. | No.                 |


## Utilities
This cog module contains server utilities that are sometimes useful, like picking a random number or a random user from the guild.

| Command    | Description                                              | Has a context menu? |
|------------|----------------------------------------------------------|---------------------|
| rand       | Generate a random number in the provided range.          | No.                 |
| randmember | Ping a random member from the guild.                     | No.                 |
| listroles  | Generate an embed with provided roles and their members. | No.                 |


## Info
This cog module contains mostly commands that display information about something. For example, displaying information about a certain user or a guild.

| Command    | Description                              | Has a context menu? |
|------------|------------------------------------------|---------------------|
| serverinfo | Display the current guild's information. | No.                 |
| userinfo   | Display a user's information.            | Yes.                |
| avatar     | Display a user's avatar.                 | No.                 |


## Fun
This cog module contains miscellaneous commands, mostly without actual purpose.

| Command | Description                                   | Has a context menu? |
|---------|-----------------------------------------------|---------------------|
| ip      | Display a random IPv4 adress.                 | No.                 |
| kys     | Kys.                                          | No.                 |
| do      | Change the bot's presence.                    | No.                 |
| fog     | Display remaining time until the fog arrives. | No.                 |