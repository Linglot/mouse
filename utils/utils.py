import discord

from settings.constants import INFO_COLOR, ERROR_COLOR, MOD_ROLES


# Just a convenient way to make error boxes
def send_error_embed(ctx, message, dm=False):
    embed = discord.Embed(description=message, colour=discord.Colour(ERROR_COLOR))
    if dm:
        ctx.author.dm_channel.send(embed=embed)
    else:
        ctx.send(embed=embed)


# Just a convenient way to make info boxes
def send_info_embed(ctx, message):
    embed = discord.Embed(description=message, colour=discord.Colour(INFO_COLOR))
    ctx.send(embed=embed)


def get_role(server, role_name):
    return discord.utils.find(lambda m: m.name.lower() == role_name.lower(), server.roles)


def get_text_channel(server, channel_name):
    return discord.utils.find(lambda m: m.name.lower() == channel_name.lower(), server.text_channels)


def get_full_name(user):
    return user.name + "#" + user.discriminator


def is_mod(member):
    return True
    #return any([role in MOD_ROLES for role in member.roles])
