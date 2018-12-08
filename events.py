from utils import can_edit_channel, get_original_name, splittable
from logger import logger


class Events:
    def __init__(self, client):
        self.bot = client

    async def on_voice_state_update(self, before, after):
        # VC user was before changing his state
        # None if he wasn't in VC before
        vc = before.voice.voice_channel

        # If user was in VC, we can edit this VC, there's no one in VC left and it was changed before
        if vc is not None and can_edit_channel(self.bot, vc) and len(vc.voice_members) == 0 and splittable(vc.name):
            await self.bot.edit_channel(vc, name=get_original_name(vc.name))
            logger.info("Removed language tag from {}".format(vc.name))

    # For logging only.
    async def on_command(self, command, ctx):
        msg = ctx.message
        logger.info('{}#{} sent \"{}\"'.format(msg.author.name, msg.author.discriminator, msg.content))


def setup(bot):
    bot.add_cog(Events(bot))
