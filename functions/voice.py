import random

from settings.config import settings
from settings.lines import text_lines
from utils.tools import *


# Command for changing VC's language in title
async def change_vc_name(bot, ctx, *args):
    # If user isn't even in VC
    if ctx.message.author is None or ctx.message.author.voice.voice_channel is None:
        embed = error_embed(text_lines['voice_channel_language']['lang_must_be_in_vc'])
        await bot.send_message(ctx.message.channel, embed=embed)
        return

    vc = ctx.message.author.voice.voice_channel

    # Permissions check
    if not can_edit_channel(bot, vc):
        embed = error_embed(text_lines['voice_channel_language']['lang_cant_edit'])
        await bot.send_message(ctx.message.channel, embed=embed)
        return

    # Since we get out name as an array of strings, we should connect 'em
    # ["lol","qwe"] -> "lol qwe"
    lang_name = " ".join(args)

    # Empty? Pass
    if len(lang_name.strip()) == 0:
        embed = error_embed(random.choice(text_lines['voice_channel_language']['lang_if_nothing']))
        await bot.send_message(ctx.message.channel, embed=embed)
        return

    # If we get "reset" then we're going to use another function
    if lang_name.strip() == "reset":
        # TODO make this gre..work again
        # await reset_lang.callback(self, ctx)
        return

    # I wish my iq were that big (20 chars max length)
    if len(lang_name) > settings['change_channel_lang']['max_lang_name_length']:
        embed = error_embed(text_lines['voice_channel_language']['lang_make_shorter'])
        await bot.send_message(ctx.message.channel, embed=embed)
        return

    # If the name could be split (or had been changed in the past, in other words)
    # when we just need to change the last part
    if splittable(vc.name):
        # This is poop code right there, TODO: rewrite
        await bot.edit_channel(vc, name="{} {} {}".format(get_original_name(vc.name), VOICE_CHANNEL_DIVIDER,
                                                          lang_name))
    # Otherwise add a suffix
    else:
        await bot.edit_channel(vc, name="{} {} {}".format(vc.name, VOICE_CHANNEL_DIVIDER, lang_name))

    info = info_embed(text_lines['voice_channel_language']['lang_were_set'].format(lang_name))
    await bot.send_message(ctx.message.channel, embed=info)

async def reset_vc_name(bot, ctx):
    if ctx.message.author is None or ctx.message.author.voice.voice_channel is None:
        embed = error_embed(text_lines['voice_channel_language']['lang_must_be_in_vc'])
        await bot.send_message(ctx.message.channel, embed=embed)
        return

    vc = ctx.message.author.voice.voice_channel
    oc_name = get_original_name(vc.name)

    # If we can't edit channel, then we can't reset its name
    if can_edit_channel(bot, vc):
        await bot.edit_channel(vc, name=oc_name)
        info = info_embed(text_lines['voice_channel_language']['lang_were_reset'].format(oc_name))
        await self.bot.send_message(ctx.message.channel, embed=info)

    else:
        embed = error_embed(text_lines['voice_channel_language']['lang_cant_edit'])
        await self.bot.send_message(ctx.message.channel, embed=embed)
