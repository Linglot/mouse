import discord
from _config import *
from discord.ext import commands
from _lines import *
from utils import *
import random


class ChatCommands:
    def __init__(self, bot):
        print("Chat commands were initialized")
        self.bot = bot

    # A command for changing language
    # Syntax is: lang
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
    # ;resetlang command
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

    # ;about command
    @commands.command(aliases=["about", "info"], pass_context=True)
    async def show_info(self, ctx):

        # Creating table
        embed = discord.Embed(colour=discord.Colour(OFF_COLOR_3),
                              description=about_desc)

        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_author(name=self.bot.user.name)
        embed.set_footer(text=version_currently.format(CURRENT_VERSION))

        embed.add_field(name=about_gh_link, value=about_gh_desc, inline=True)
        embed.add_field(name=about_inv_link, value=about_inv_desc, inline=True)

        await self.bot.send_message(ctx.message.channel, embed=embed)

    # ;version command
    @commands.command(aliases=["version", "ver"], pass_context=True)
    async def show_version(self, ctx):
        # Creating table
        embed = discord.Embed(title=version_currently.format(CURRENT_VERSION),
                              colour=discord.Colour(OFF_COLOR_3))
        embed.set_footer(text=version_footer.format(self.bot.user.name), icon_url=self.bot.user.avatar_url)

        await self.bot.send_message(ctx.message.channel, embed=embed)


def setup(bot):
    bot.add_cog(ChatCommands(bot))
