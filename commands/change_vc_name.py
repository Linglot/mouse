import random

from discord.ext import commands

from _config import settings
from _lines import text_lines
from utils import *


class ChangeLanguage:
    def __init__(self, bot):
        self.bot = bot

    # Command for changing VC's language in title
    # Syntax: ;lang Language Name
    @commands.command(aliases=["lang", "l"], pass_context=True)
    async def change_channel_lang(self, ctx, *args):

        # If user isn't even in VC
        if ctx.message.author is None or ctx.message.author.voice.voice_channel is None:
            embed = error_embed(text_lines['voice_channel_language']['lang_must_be_in_vc'])
            await self.bot.send_message(ctx.message.channel, embed=embed)
            return

        vc = ctx.message.author.voice.voice_channel

        # Permissions check
        if not can_edit_channel(self.bot, vc):
            embed = error_embed(text_lines['voice_channel_language']['lang_cant_edit'])
            await self.bot.send_message(ctx.message.channel, embed=embed)
            return

        # Since we get out name as an array of strings, we should connect 'em
        # ["lol","qwe"] -> "lol qwe"
        lang_name = " ".join(args)

        # Empty? Pass
        if len(lang_name.strip()) == 0:
            embed = error_embed(random.choice(text_lines['voice_channel_language']['lang_if_nothing']))
            await self.bot.send_message(ctx.message.channel, embed=embed)
            return

        # If we get "reset" then we're going to use another function
        if lang_name.strip() == "reset":
            await self.reset_lang.callback(self, ctx)
            return

        # I wish my iq were that big (20 chars max length)
        if len(lang_name) > settings['change_channel_lang']['max_lang_name_length']:
            embed = error_embed(text_lines['voice_channel_language']['lang_make_shorter'])
            await self.bot.send_message(ctx.message.channel, embed=embed)
            return

        # If the name could be split (or had been changed in the past, in other words)
        # when we just need to change the last part
        if splittable(vc.name):
            # This is poop code right there, TODO: rewrite
            await self.bot.edit_channel(vc, name="{} {} {}".format(get_original_name(vc.name), VOICE_CHANNEL_DIVIDER,
                                                                   lang_name))
        # Otherwise add a suffix
        else:
            await self.bot.edit_channel(vc, name="{} {} {}".format(vc.name, VOICE_CHANNEL_DIVIDER, lang_name))

        info = info_embed(text_lines['voice_channel_language']['lang_were_set'].format(lang_name))
        await self.bot.send_message(ctx.message.channel, embed=info)

    # TODO: Remove code duplication with VC behaviour's function
    # Command for removing language name from VC's name
    # Syntax: ;resetlang
    @commands.command(aliases=["resetlang", "rl"], pass_context=True)
    async def reset_lang(self, ctx):
        if ctx.message.author is None or ctx.message.author.voice.voice_channel is None:
            embed = error_embed(text_lines['voice_channel_language']['lang_must_be_in_vc'])
            await self.bot.send_message(ctx.message.channel, embed=embed)
            return

        vc = ctx.message.author.voice.voice_channel
        oc_name = get_original_name(vc.name)

        # If we can't edit channel, then we can't reset its name
        if can_edit_channel(self.bot, vc):
            await self.bot.edit_channel(vc, name=oc_name)
            info = info_embed(text_lines['voice_channel_language']['lang_were_reset'].format(oc_name))
            await self.bot.send_message(ctx.message.channel, embed=info)

        else:
            embed = error_embed(text_lines['voice_channel_language']['lang_cant_edit'])
            await self.bot.send_message(ctx.message.channel, embed=embed)


def setup(bot):
    bot.add_cog(ChangeLanguage(bot))
