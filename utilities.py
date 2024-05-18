from discord.ext import commands

def ensure_user_is_in_database():
    async def predicate(ctx):
        # Check if the user exists in the database
        user = await ctx.bot.db.fetchrow('SELECT 1 FROM users WHERE user_id = $1', ctx.author.id)

        # If the user doesn't exist, insert them into the database
        if not user:
            await ctx.bot.db.execute('INSERT INTO users (user_id) VALUES ($1)', ctx.author.id)

        # Continue with the command execution
        return True

    return commands.check(predicate)