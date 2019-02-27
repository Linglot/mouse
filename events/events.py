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
            if joined_to.category.id == settings['voice']['lang_category_id'] and not is_mod(
                    member):
                print(member.name + ' joined')
                name = VoiceCommands.get_original_name(joined_to.name)
                channel = get_text_channel(server, name + '-text')
                if channel is not None:
                    await channel.set_permissions(member, reason='Joined vc',
                                                  read_messages=True,
                                                  send_messages=True)

        # Leaving events
        if left_from is not None:

            # Channel renaming if everyone has left
            if VoiceCommands.can_edit(left_from) and len(left_from.members) == 0 and VoiceCommands.splittable(
                    left_from.name):
                await VoiceCommands.reset_name(left_from)
                logger.info(text_lines['logging']['lang_removed'].format(left_from.name))

            # Removing access to the channel if it was a language related one
            if left_from.category.id == settings['voice']['lang_category_id'] and not is_mod(
                    member) and left_from.id != joined_to.id:
                print(member.name + ' left')
                name = VoiceCommands.get_original_name(left_from.name)
                channel = get_text_channel(server, name + '-text')
                if channel is not None:
                    await channel.set_permissions(member, reason='Left vc',
                                                  read_messages=False,
                                                  send_messages=False)

    @staticmethod
    async def on_command(ctx):
        msg = ctx.message
        logger.info(
            '{}#{} sent \"{}\" in #{}'.format(msg.author.name, msg.author.discriminator, msg.content, ctx.channel))


def setup(bot):
    bot.add_cog(Events(bot))
