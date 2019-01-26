from discord.ext.commands import Bot

from settings.config import TOKEN, PREFIX

bot = Bot(command_prefix=PREFIX)

modules = ['commands']#, 'events']


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
#bot.run(TOKEN_SERVER)
