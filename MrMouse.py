# Work with Python 3.6
from discord.ext.commands import Bot
from _config import *

bot = Bot(command_prefix=PREFIX)

modules = ['chat_commands', 'vc_behaviour']


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
        print("Extensions: {} module was loaded.".format(extension))
        bot.load_extension(extension)

bot.run(TOKEN, bot=True, reconnect=True)

# TODO: make versions
# TODO: backups
# TODO: roles merge search
