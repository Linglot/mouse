from discord.ext.commands import Bot

from settings.config import TOKEN, PREFIX

bot = Bot(command_prefix=PREFIX)

extensions = [
    # Commands
    'cogs.info',
    'cogs.roles',
    'cogs.voice',

    # Events
    'events.events',
    'events.on_error'
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