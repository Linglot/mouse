from discord.ext.commands import Bot

from settings.config import TOKEN, PREFIX, TOKEN_SERVER

bot = Bot(command_prefix=PREFIX)

modules = ['commands', 'events']


@bot.event
async def on_ready():
    print('Logged in as {} (Id: {})'.format(bot.user.name, bot.user.id))


if __name__ == "__main__":
    try:
        print("Removing default help...")
        bot.remove_command('help')
    finally:
        print("Default help command was removed")

    # Loading modules
    for extension in modules:
        bot.load_extension(extension)
        print("Extensions: {} module was loaded.".format(extension))

bot.run(TOKEN)

"""
https://gist.github.com/EvieePy/d78c061a4798ae81be9825468fe146be
https://discordpy.readthedocs.io/en/rewrite/ext/commands/api.html#context
https://discordpy.readthedocs.io/en/rewrite/api.html#discord.Member

make commands.py and events.py RIP
move cogs and events to functions
do a mini refactor in utils

"""
