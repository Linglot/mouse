from settings.config import *
from settings.lines import text_lines
from utils.tools import *


# Simple bot-info command
# Shows discord invite link, git, and some bot-related info
async def show_about(bot, channel):
    # Creating table
    embed = discord.Embed(colour=discord.Colour(OFF_COLOR_3),
                          description=text_lines['about']['about_desc'])

    embed.set_thumbnail(url=bot.user.avatar_url)
    embed.set_author(name=bot.user.name)
    embed.set_footer(text=text_lines['version']['version_currently'].format(CURRENT_VERSION))

    embed.add_field(name=text_lines['about']['about_gh_link'], value=text_lines['about']['about_gh_desc'],
                    inline=True)
    embed.add_field(name=text_lines['about']['about_inv_link'], value=text_lines['about']['about_inv_desc'],
                    inline=True)

    await bot.send_message(channel, embed=embed)


# Version command
async def show_version(bot, channel):
    # Creating table
    embed = discord.Embed(title=text_lines['version']['version_currently'].format(CURRENT_VERSION),
                          colour=discord.Colour(OFF_COLOR_3))
    embed.set_footer(text=text_lines['version']['version_footer'].format(bot.user.name),
                     icon_url=bot.user.avatar_url)

    await bot.send_message(channel, embed=embed)
