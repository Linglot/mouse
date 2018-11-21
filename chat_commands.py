from discord.ext import commands
import random
from _lines import *
from utils import *


class ChatCommands:
    def __init__(self, bot):
        print("Chat commands were initialized")
        self.bot = bot

    # ;lang command
    @commands.command(aliases=["lang", "l"], pass_context=True)
    async def change_channel_lang(self, ctx, *args):

        # If guys isn't in VC
        if ctx.message.author is None or ctx.message.author.voice.voice_channel is None:
            await self.bot.send_message(ctx.message.channel, lang_must_be_in_vc)
            return

        vc = ctx.message.author.voice.voice_channel

        # Permissions check
        if not can_edit(self.bot, vc):
            await self.bot.send_message(ctx.message.channel, lang_cant_edit)
            return

        # Since we get out name as an array of strings, we should connect 'em
        # ["lol","qwe"] -> "lol qwe"
        lang_name = " ".join(args)

        # Empty? Pass
        if len(lang_name.strip()) == 0:
            await self.bot.send_message(ctx.message.channel, random.choice(lang_if_nothing))
            return

        # Then we're use another function
        if lang_name.strip() == "reset":
            await self.reset_lang.callback(self, ctx)
            return

        # I wish my iq were that bit (20 char. max length)
        if len(lang_name) > 20:
            await self.bot.send_message(ctx.message.channel, lang_make_shorter)
            return

        # If the name could be splitted (or had been changed in the past, in other words)
        # when we just need to change the last part
        if splittable(vc.name):
            # This is poop code right there, TODO: rewrite
            await self.bot.edit_channel(vc, name="{} {} {}".format(get_original_name(vc.name), VOICE_CHANNEL_DIVIDER,
                                                                   lang_name))
        # Otherwise add a suffix
        else:
            await self.bot.edit_channel(vc, name="{} {} {}".format(vc.name, VOICE_CHANNEL_DIVIDER, lang_name))
        await self.bot.send_message(ctx.message.channel, lang_were_set.format(lang_name))

    # TODO: Remove code duplication with VC behaviour's function
    @commands.command(aliases=["resetlang", "rl"], pass_context=True)
    async def reset_lang(self, ctx):
        if ctx.message.author is None or ctx.message.author.voice.voice_channel is None:
            await self.bot.send_message(ctx.message.channel, lang_must_be_in_vc)
            return

        vc = ctx.message.author.voice.voice_channel
        oc_name = get_original_name(vc.name)

        try:
            await self.bot.edit_channel(vc, name=oc_name)
        finally:
            await self.bot.send_message(ctx.message.channel, lang_were_reset.format(oc_name))


def setup(bot):
    bot.add_cog(ChatCommands(bot))
