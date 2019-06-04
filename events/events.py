from cogs.voice import VoiceCommands
from settings.config import settings
from utils.logger import logger
from utils.utils import get_text_channel, is_mod


# This class designed to control all the possible events
class Events:
    def __init__(self, bot):
        self.bot = bot

    # This is called every time a used joins or left any VC
    async def on_voice_state_update(self, member, before, after):
        # VC user was before changing his state
        # None if he wasn't in VC before
        server = member.guild
        left_from = before.channel if before.channel is not None else None
        joined_to = after.channel if after.channel is not None else None

        #
        #
        # There's some code related to language voice channels feature, but Yata said it's not needed anymore
        # but I didn't have time to get rid of it. It wont work anyways, cuz it check the ID every time (which is in setting)
        #
        #

        # Joining events
        if joined_to is not None:
            # Language related VCs
            if self.should_show_langvc(joined_to, member):
                await self.set_permissions_to(server, joined_to, member, True, reason='Joined to VC')

        # Leaving events
        if left_from is not None:

            # Resets VC's name if there's no users left in it.
            if VoiceCommands.can_edit(left_from) and len(left_from.members) == 0 and VoiceCommands.splittable(
                    left_from.name):
                await VoiceCommands.reset_name(left_from)

            # Removing access to the channel if it was a language related one
            if self.should_hide_langvc(left_from, joined_to, member):
                await self.set_permissions_to(server, left_from, member, False, reason='Left from VC')

    # Sets read&write permissions for a specified channel with given value. Returns true if succeed
    async def set_permissions_to(self, server, channel, member, value, reason=''):
        name = VoiceCommands.get_original_name(channel.name)
        channel = get_text_channel(server, name + '-text')
        if channel is not None:
            await channel.set_permissions(member, reason=reason, read_messages=value, send_messages=value)
            return True

        return False

    # Returns true if a language-related channel is not visible (aka user joins for the first time)
    def should_show_langvc(self, joined_to, member) -> bool:
        return joined_to.category is not None \
               and joined_to.category.id == settings['voice']['lang_category_id'] \
               and not is_mod(member)

    # Returns true if a language-related channel is visible (aka the permissions have been given in the past)
    def should_hide_langvc(self, left_from, joined_to, member) -> bool:
        # I think I'll be killed one day because of this if
        return left_from.category is not None \
               and left_from.category.id == settings['voice']['lang_category_id'] \
               and not is_mod(member) \
               and left_from.id != (joined_to.id if joined_to is not None else None)

    # Basic log event for every command
    @staticmethod
    async def on_command(ctx):
        msg = ctx.message
        logger.info(
            '{}#{} sent \"{}\" in #{}'.format(msg.author.name, msg.author.discriminator, msg.content, ctx.channel))


def setup(bot):
    bot.add_cog(Events(bot))
