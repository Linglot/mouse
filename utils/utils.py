import discord

# If we get an array of 2 (or more, somehow) then it's splittable
from settings.constants import INFO_COLOR, ERROR_COLOR


# Just a convenient way to make error boxes
def error_embed(message):
    embed = discord.Embed(description=message, colour=discord.Colour(ERROR_COLOR))
    return embed


# Just a convenient way to make info boxes
def info_embed(message):
    embed = discord.Embed(description=message, colour=discord.Colour(INFO_COLOR))
    return embed


def get_role(server, role_name):
    return discord.utils.find(lambda m: m.name.lower() == role_name.lower(), server.roles)


def get_text_channel(server, channel_name):
    return discord.utils.find(lambda m: m.name.lower() == channel_name.lower(), server.text_channels)


def get_full_name(user):
    return user.name + "#" + user.discriminator
