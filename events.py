from utils import *
from logger import logger


# Class for voice chat related events
class Events:
    def __init__(self, client):
        self.bot = client

    async def on_voice_state_update(self, before, after):
        # VC user came from(!)
        vc = before.voice.voice_channel

        # What would I change, if the user isn't even in VC?
        # Check the permissions at first, and the number of people in the channel

        if vc is not None and can_edit_channel(self.bot, vc) and len(vc.voice_members) == 0 and splittable(vc.name):
            await self.bot.edit_channel(vc, name=get_original_name(vc.name))
            logger.info("Removed language from {}".format(vc.name))


def setup(bot):
    bot.add_cog(Events(bot))
