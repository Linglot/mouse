from discord.ext.commands import Bot
from _config import *

bot = Bot(command_prefix=PREFIX)

# TODO: k python said fuk you so we should be back to the previous version but exclude the logic from there.
modules = ['commands/about',
           'commands/change_vc_name',
           'commands/combine_search',
           'commands/version',
           'events']


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
