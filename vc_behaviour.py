from utils import *


# Class for voice chat related events
class VCBehaviour:
    def __init__(self, client):
        self.bot = client

    async def on_voice_state_update(self, before, after):
        # VC user came from(!)
        vc = before.voice.voice_channel

        # What would I change, if he's wasn't even in VC?
        if vc is not None:
            # Check the permissions at first, and the number of people in the channel
            if can_edit_channel(self.bot, vc):
                if len(vc.voice_members) == 0 and splittable(vc.name):
                    await self.bot.edit_channel(vc, name=get_original_name(vc.name))
                    print("Removed language from {}".format(vc.name))
                else:
                    print("{} left from {} but there's no need to edit".format(before.name, vc.name))
            else:
                print("{} left from {} but I can't edit anyways ¯\_(ツ)_/¯".format(before.name, vc.name))


def setup(bot):
    bot.add_cog(VCBehaviour(bot))
