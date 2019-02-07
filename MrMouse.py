from discord.ext.commands import Bot

from settings.config import TOKEN, PREFIX, TOKEN_SERVER

bot = Bot(command_prefix=PREFIX)

# initial_extensions = ['commands', 'events']
extensions = [
    # Commands related
    'cogs.info',

    # Events
    #'events.events',
    #'events.on_error'
]


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
    for extension in extensions:
        bot.load_extension(extension)
        print("Extensions: {} module was loaded.".format(extension))

bot.run(TOKEN, bot=True, reconnect=True, fetch_offline_members=True)

"""
https://gist.github.com/EvieePy/d78c061a4798ae81be9825468fe146be
https://discordpy.readthedocs.io/en/rewrite/ext/commands/api.html#context
https://discordpy.readthedocs.io/en/rewrite/api.html#discord.Member

make commands.py and events.py RIP
move cogs and events to cogs
do a mini refactor in utils

"""
