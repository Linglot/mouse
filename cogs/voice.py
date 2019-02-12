from discord.ext import commands

from settings.config import settings
from settings.lines import text_lines
from utils.utils import *


class VoiceCommands:

    def __init__(self, bot):
        self.bot = bot

    # Command for changing VC's language in title
    # Syntax: ;lang Language Name
    @commands.command(name='language', aliases=["lang", "l"])
    @commands.guild_only()
    async def change_vc_name(self, ctx, *args):
        user = ctx.author
        vc = ctx.author.voice.channel
        lang_name = " ".join(args).title()

        # If user isn't even in VC we tell they that they should be in one.
        if not self.user_in_vc(user):
            await ctx.send(embed=error_embed(text_lines['voice']['change']['must_be_in_vc']))
            return

        # Permissions check
        if not self.can_edit(self.bot, vc):
            await ctx.send(embed=error_embed(text_lines['voice']['change']['cant_edit']))
            return

        # Empty? Pass
        if len(lang_name.strip()) == 0:
            await ctx.send(embed=error_embed(text_lines['voice_channel_language']['lang_if_nothing']))
            return

        # If we get "reset" then we're going to use another function
        if lang_name.strip() == "reset":
            # TODO
            # await self.reset_vc_name(.....)
            return

        # I wish my iq were that big (20 chars max length)
        if len(lang_name) > settings['voice']['max_length']:
            await ctx.send(embed=error_embed(text_lines['voice']['change']['shorter']))
            return

        # If the name could be split (or had been changed before, in other words)
        # then we just need to change the last part
        if self.splittable(vc.name):
            # This is poop code right here
            # TODO: rewrite, but later
            await vc.edit(name=text_lines['voice']['format'].format(
                get_original_name(vc.name), VOICE_CHANNEL_DIVIDER, lang_name))
        # Otherwise add a suffix
        else:
            await vc.edit(name=text_lines['voice']['format'].format(vc.name, VOICE_CHANNEL_DIVIDER, lang_name))

        info = info_embed(text_lines['voice']['change']['done'].format(lang_name))
        await ctx.send(embed=info)

    # async def reset_vc_name(bot, user, channel, vc):
    #     # If user isn't even in VC we tell they that they should be in one.
    #     if not user_in_vc(user, vc):
    #         embed = error_embed(text_lines['voice_channel_language']['lang_must_be_in_vc'])
    #         await bot.send_message(channel, embed=embed)
    #         return
    #
    #     # If we can't edit channel, then we can't reset its name
    #     if can_edit_channel(bot, vc):
    #         await _reset_channel_name(bot, vc)
    #         info = info_embed(
    #             text_lines['voice_channel_language']['lang_were_reset'].format(get_original_name(vc.name)))
    #         await bot.send_message(channel, embed=info)
    #
    #     else:
    #         embed = error_embed(text_lines['voice_channel_language']['lang_cant_edit'])
    #         await bot.send_message(channel, embed=embed)
    #
    # # Used for removing code duplicating in reset VC's name cogs
    # # Because we have one as a command and other as an event when channels gets empty
    # async def _reset_channel_name(bot, vc):
    #     oc_name = get_original_name(vc.name)
    #     await bot.edit_channel(vc, name=oc_name)
    #     return True

    # Static helpful methods after

    # Return true if given user in VC
    @staticmethod
    def user_in_vc(member):
        if member.voice is None:
            return False
        return True

    # Return true if the bot has "manage channel" permission, otherwise false
    @staticmethod
    def can_edit(bot, channel):
        return channel.permissions_for(bot.user).manage_channels

    # Returns true if VC's name was changed
    @staticmethod
    def splittable(vc_name):
        return len(vc_name.split(" {} ".format(VOICE_CHANNEL_DIVIDER))) >= 2


def setup(bot):
    bot.add_cog(VoiceCommands(bot))
