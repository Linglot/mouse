from _config import VOICE_CHANNEL_DIVIDER
import more_itertools


# If we get an array of 2 (or more, somehow) then it's splittable
def splittable(name):
    return len(name.split(" {} ".format(VOICE_CHANNEL_DIVIDER))) >= 2


# "Name | Lang" -> "Name"
def get_original_name(name):
    return name.split(" {} ".format(VOICE_CHANNEL_DIVIDER))[0]


# Moki will kill me, if he sees this.
def can_edit_channel(bot, channel):
    return channel.permissions_for(channel.server.get_member(bot.user.id)).manage_channels


# Divides list into N evenly-sized chunks
def create_chunks(list_to_divide, number_of_chunks):
    return [list(c) for c in more_itertools.divide(number_of_chunks, list_to_divide)]


# Add a … symbol if the is longer than "limit"
def add_dots(string, limit):
    # "…" " " - 3 dots + 2x unbreakable spaces (alt+0160)
    return (string[:limit] + '…  ') if len(string) > limit else string
