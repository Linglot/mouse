from settings.config import *
from settings.lines import text_lines
from utils.tools import *


# Simple bot-info command
# Shows discord invite link, git, and some bot-related info
async def show_info(bot, ctx):
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

    await bot.send_message(ctx.message.channel, embed=embed)
