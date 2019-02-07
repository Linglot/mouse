from cogs.voice import _reset_channel_name
from settings.lines import text_lines
from utils.logger import logger
from utils.tools import can_edit_channel, splittable, error_embed


class Events:
    def __init__(self, client):
        self.bot = client

    async def on_voice_state_update(self, member, before, after):
        # VC user was before changing his state
        # None if he wasn't in VC before
        vc = before.voice_channel

        # If user was in VC, we can edit this VC, there's no one in VC left and it was changed before
        if vc is not None and can_edit_channel(self.bot, vc) and len(vc.voice_members) == 0 and splittable(vc.name):
            await _reset_channel_name(self.bot, vc)
            logger.info(text_lines['logging']['lang_removed'].format(vc.name))

    @staticmethod
    async def on_command(ctx):
        msg = ctx.message
        logger.info('{}#{} sent \"{}\" in #{}'.format(msg.author.name, msg.author.discriminator, msg.content, ctx.channel))


def setup(bot):
    bot.add_cog(Events(bot))
