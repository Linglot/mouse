from cogs.voice import VoiceCommands
from settings.lines import text_lines
from utils.logger import logger


class Events:
    def __init__(self, bot):
        self.bot = bot

    async def on_voice_state_update(self, member, before, after):
        # VC user was before changing his state
        # None if he wasn't in VC before
        vc = before.channel

        # If user was in VC, we can edit this VC, there's no one in VC left and it was changed before
        if vc is not None and \
                VoiceCommands.can_edit(self.bot, vc) and \
                len(vc.members) == 0 and VoiceCommands.splittable(vc.name):
            # await _reset_channel_name(self.bot, vc)
            logger.info(text_lines['logging']['lang_removed'].format(vc.name))

    @staticmethod
    async def on_command(ctx):
        msg = ctx.message
        logger.info(
            '{}#{} sent \"{}\" in #{}'.format(msg.author.name, msg.author.discriminator, msg.content, ctx.channel))


def setup(bot):
    bot.add_cog(Events(bot))
