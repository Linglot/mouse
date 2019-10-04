from discord.ext import commands

from settings.config import settings, VOICE_CHANNEL_DIVIDER
from settings.lines import text_lines

from utils.utils import send_error_embed, send_info_embed


class VoiceCommands(commands.Cog):
    RESET_LANG_ALIASES = ['resetlang', 'rl', 'reset']

    def __init__(self, bot):
        self.bot = bot

    # Command for changing VC's language in title
    # Syntax: ;lang Language Name
    @commands.command(name='language', aliases=['lang', 'l', *RESET_LANG_ALIASES])
    @commands.guild_only()
    async def change_vc_name(self, ctx, *args):
        lang_name = " ".join(args).title()

        # If user isn't even in VC we tell they that they should be in one.
        if not self.user_in_vc(ctx.author):
            await send_error_embed(ctx, text_lines['voice']['change']['must_be_in_vc'])
            return False

        # Permissions check
        if not self.can_edit(ctx.author.voice.channel):
            await send_error_embed(ctx, text_lines['voice']['change']['cant_edit'])
            return False

        vc = ctx.author.voice.channel

        # If we get "reset" then we're going to use another function
        if lang_name.strip() == "reset" or ctx.invoked_with in self.RESET_LANG_ALIASES:
            await self.reset_name(vc)
            await send_info_embed(ctx, text_lines['voice']['reset'].format(self.get_original_name(vc.name)))
            return

        # Empty? Pass
        if len(lang_name.strip()) == 0:
            await send_error_embed(ctx, text_lines['voice']['change']['empty'])
            return

        # I wish my iq were that big (20 chars max length)
        if len(lang_name) > settings['voice']['max_length']:
            await send_error_embed(ctx, text_lines['voice']['change']['shorter'])
            return

        # If the name could be split (or had been changed before, in other words)
        # then we just need to change the last part
        if self.splittable(vc.name):
            await vc.edit(name=text_lines['voice']['format'].format(
                self.get_original_name(vc.name), VOICE_CHANNEL_DIVIDER, lang_name))
        # Otherwise add a suffix
        else:
            await vc.edit(name=text_lines['voice']['format'].format(
                vc.name, VOICE_CHANNEL_DIVIDER, lang_name))

        await send_info_embed(ctx, text_lines['voice']['change']['done'].format(lang_name))

    # Static helpful methods after

    # Used for removing code duplicating in reset VC's name cogs
    # Because we have one as a command and other as an event when channels gets empty
    @staticmethod
    async def reset_name(vc):
        oc_name = VoiceCommands.get_original_name(vc.name)
        await vc.edit(name=oc_name)
        return True

    # Return true if given user in VC
    @staticmethod
    def user_in_vc(member):
        if member is None or member.voice is None:
            return False
        return True

    # Return true if the bot has "manage channel" permission, otherwise false
    @staticmethod
    def can_edit(channel):
        return channel.permissions_for(channel.guild.me).manage_channels

    # Returns true if VC's name was changed
    @staticmethod
    def splittable(vc_name):
        return len(vc_name.split(" {} ".format(VOICE_CHANNEL_DIVIDER))) >= 2

    # "Name | Lang" -> "Name"
    @staticmethod
    def get_original_name(vc_name):
        return vc_name.split(" {} ".format(VOICE_CHANNEL_DIVIDER))[0]


def setup(bot):
    bot.add_cog(VoiceCommands(bot))
