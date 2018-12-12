import random

from settings.config import settings
from settings.lines import text_lines
from utils.tools import *


# Command for changing VC's language in title
async def change_vc_name(bot, user, channel, vc, lang_name):
    # If user isn't even in VC we tell they that they should be in one.
    if not user_in_vc(user, vc):
        embed = error_embed(text_lines['voice_channel_language']['lang_must_be_in_vc'])
        await bot.send_message(channel, embed=embed)
        return

    # Permissions check
    if not can_edit_channel(bot, vc):
        embed = error_embed(text_lines['voice_channel_language']['lang_cant_edit'])
        await bot.send_message(channel, embed=embed)
        return

    # Empty? Pass
    if len(lang_name.strip()) == 0:
        embed = error_embed(random.choice(text_lines['voice_channel_language']['lang_if_nothing']))
        await bot.send_message(channel, embed=embed)
        return

    # If we get "reset" then we're going to use another function
    if lang_name.strip() == "reset":
        # TODO make this gre..work again
        # await reset_lang.callback(self, ctx)
        return

    # I wish my iq were that big (20 chars max length)
    if len(lang_name) > settings['change_channel_lang']['max_lang_name_length']:
        embed = error_embed(text_lines['voice_channel_language']['lang_make_shorter'])
        await bot.send_message(channel, embed=embed)
        return

    # If the name could be split (or had been changed in the past, in other words)
    # when we just need to change the last part
    if splittable(vc.name):
        # This is poop code right there
        # TODO: rewrite, but later
        await bot.edit_channel(vc, name="{} {} {}".format(get_original_name(vc.name), VOICE_CHANNEL_DIVIDER,
                                                          lang_name))
    # Otherwise add a suffix
    else:
        await bot.edit_channel(vc, name="{} {} {}".format(vc.name, VOICE_CHANNEL_DIVIDER, lang_name))

    info = info_embed(text_lines['voice_channel_language']['lang_were_set'].format(lang_name))
    await bot.send_message(channel, embed=info)


async def reset_vc_name(bot, user, channel, vc):
    # If user isn't even in VC we tell they that they should be in one.
    if not user_in_vc(user, vc):
        embed = error_embed(text_lines['voice_channel_language']['lang_must_be_in_vc'])
        await bot.send_message(channel, embed=embed)
        return

    # If we can't edit channel, then we can't reset its name
    if can_edit_channel(bot, vc):
        await _reset_channel_name(bot, vc)
        info = info_embed(text_lines['voice_channel_language']['lang_were_reset'].format(get_original_name(vc.name)))
        await bot.send_message(channel, embed=info)

    else:
        embed = error_embed(text_lines['voice_channel_language']['lang_cant_edit'])
        await bot.send_message(channel, embed=embed)


# Used for removing code duplicating in reset VC's name functions
# Because we have one as a command and other as an event when channels gets empty
async def _reset_channel_name(bot, vc):
    oc_name = get_original_name(vc.name)
    await bot.edit_channel(vc, name=oc_name)
