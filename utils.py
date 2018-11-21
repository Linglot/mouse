from _config import VOICE_CHANNEL_DIVIDER

# If we get an array of 2 (or more, somehow) then it's splittable
def splittable(name):
    return len(name.split(" {} ".format(VOICE_CHANNEL_DIVIDER))) >= 2

# "Name | Lang" -> "Name"
def get_original_name(name):
    return name.split(" {} ".format(VOICE_CHANNEL_DIVIDER))[0]

# Moki will kill me, if he sees this.
def can_edit(bot, channel):
    return channel.permissions_for(channel.server.get_member(bot.user.id)).manage_channels