import discord

from settings.config import CURRENT_VERSION, OFF_COLOR_3
from settings.lines import text_lines


# Version command
async def show_version(bot, ctx):
    # Creating table
    embed = discord.Embed(title=text_lines['version']['version_currently'].format(CURRENT_VERSION),
                          colour=discord.Colour(OFF_COLOR_3))
    embed.set_footer(text=text_lines['version']['version_footer'].format(bot.user.name),
                     icon_url=bot.user.avatar_url)

    await bot.send_message(ctx.message.channel, embed=embed)
