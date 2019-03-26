from cogs.voice import VoiceCommands
from settings.config import settings
from settings.lines import text_lines
from utils.logger import logger
from utils.utils import get_text_channel, is_mod


class Events:
    def __init__(self, bot):
        self.bot = bot

    async def on_voice_state_update(self, member, before, after):
        # VC user was before changing his state
        # None if he wasn't in VC before
        server = member.guild
        left_from = before.channel if before.channel is not None else None
        joined_to = after.channel if after.channel is not None else None

        # Joining events
        if joined_to is not None:
            # Language related VCs
            if self.__lang_vc_hidden(joined_to, member):
                await self.__set_permissions(server, joined_to, member, True, reason='Joined to VC')

        # Leaving events
        if left_from is not None:

            # Rename channel to its original name if everyone has left
            await self.__reset_name(left_from)

            # Removing access to the channel if it was a language related one
            if self.__lang_vc_visible(left_from, joined_to, member):
                await self.__set_permissions(server, left_from, member, False, reason='Left from VC')

    # Resets VC's name if there's no users left in it.
    async def __reset_name(self, left_from):
        if VoiceCommands.can_edit(left_from) and len(left_from.members) == 0 and VoiceCommands.splittable(
                left_from.name):
            await VoiceCommands.reset_name(left_from)
            logger.info(text_lines['logging']['lang_removed'].format(left_from.name))

    # Sets read&write permissions for a specified channel with given value. Returns true if succeed
    async def __set_permissions(self, server, channel, member, value, reason=''):
        name = VoiceCommands.get_original_name(channel.name)
        channel = get_text_channel(server, name + '-text')
        if channel is not None:
            await channel.set_permissions(member, reason=reason, read_messages=value, send_messages=value)
            return True

        return False

    # Returns true if a language-related channel is not visible (aka user joins for the first time)
    def __lang_vc_hidden(self, joined_to, member) -> bool:
        if joined_to.category is not None \
                and joined_to.category.id == settings['voice']['lang_category_id'] \
                and not is_mod(member):
            return True

        return False

    # Returns true if a language-related channel is visible (aka the permissions have been given in the past)
    def __lang_vc_visible(self, left_from, joined_to, member) -> bool:
        # I think I'll be killed one day because of this if
        if left_from.category is not None \
                and left_from.category.id == settings['voice']['lang_category_id'] \
                and not is_mod(member) \
                and left_from.id != (joined_to.id if joined_to is not None else None):
            return True

        return False

    # Basic log event for every command
    @staticmethod
    async def on_command(ctx):
        msg = ctx.message
        logger.info(
            '{}#{} sent \"{}\" in #{}'.format(msg.author.name, msg.author.discriminator, msg.content, ctx.channel))


def setup(bot):
    bot.add_cog(Events(bot))
