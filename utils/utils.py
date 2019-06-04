import discord

from settings.constants import INFO_COLOR, ERROR_COLOR, MOD_ROLES


#
# Some commands that help all across the code
#


# Just a convenient way to make error boxes
# If dm is true the error message will be sent in user's DMs
async def send_error_embed(ctx, message, dm=False):
    embed = discord.Embed(description=message, colour=discord.Colour(ERROR_COLOR))
    if dm:
        await ctx.author.dm_channel.send(embed=embed)
    else:
        await ctx.send(embed=embed)


# Just a convenient way to make info boxes
async def send_info_embed(ctx, message):
    embed = discord.Embed(description=message, colour=discord.Colour(INFO_COLOR))
    await ctx.send(embed=embed)

# Getting a Role class by its name
# Assuming that the name of the role is correct
def get_role(server, role_name):
    return discord.utils.find(lambda m: m.name.lower() == role_name.lower(), server.roles)

# Getting a Channel class by its name
# Assuming that the name of the channel is correct
def get_text_channel(server, channel_name):
    return discord.utils.find(lambda m: m.name.lower() == channel_name.lower(), server.text_channels)

# Giving the full login (not server-only related nickname) and his discriminator (those 4 numbers)
def get_full_name(user):
    return user.name + "#" + user.discriminator

# Returns true if you're a mod (wow)
def is_mod(member):
    return any([role in MOD_ROLES for role in member.roles])
