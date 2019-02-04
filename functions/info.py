from settings.constants import CURRENT_VERSION
from settings.lines import text_lines
from utils.tools import *


# async def less_than(bot, server, channel, x):
#
# async def top10(self, ctx):

# Server info command. Shows as much as it can.
async def server_info(bot, server, channel):
    roleless = [member for member in server.members if len(member.roles) == 1]

    if len(server.features) > 0:
        features = ", ".join(server.features)
    else:
        features = "None"

    if server.default_channel is not None:
        default_channel = server.default_channel.name
    else:
        default_channel = "None"



    # Creating table
    embed = discord.Embed(colour=discord.Colour(INFO_COLOR))

    embed.set_thumbnail(url=server.icon_url)
    embed.set_author(name=server.name)

    embed.add_field(name="id", value=server.id, inline=True)
    embed.add_field(name="region", value=server.region, inline=True)
    embed.add_field(name="roles", value=str(len(server.roles)) + " roles", inline=True)
    embed.add_field(name="channels", value=str(len(server.channels)) + " channels", inline=True)
    embed.add_field(name="owner", value=server.owner.name + "#" + server.owner.discriminator, inline=True)
    embed.add_field(name="features", value=features, inline=True)
    embed.add_field(name="default_channel", value=default_channel, inline=True)
    embed.add_field(name="created_at", value=server.created_at.strftime("%H:%M:%S at %d %b %Y"), inline=True)
    embed.add_field(name="Members", value="{} Members, {} without any roles".format(len(server.members), len(roleless)), inline=True)
    embed.add_field(name="emojis", value="here will be the list", inline=False)

    await bot.send_message(channel, embed=embed)


# Simple bot-info command
# Shows discord invite link, git, and some bot-related info
async def show_about(bot, channel):
    # Creating table
    embed = discord.Embed(colour=discord.Colour(INFO_COLOR),
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
                          colour=discord.Colour(INFO_COLOR))
    embed.set_footer(text=text_lines['version']['version_footer'].format(bot.user.name),
                     icon_url=bot.user.avatar_url)

    await bot.send_message(channel, embed=embed)
