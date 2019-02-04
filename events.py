from functions.voice import _reset_channel_name
from settings.lines import text_lines
from utils.logger import logger
from utils.tools import can_edit_channel, get_original_name, splittable, error_embed


class Events:
    def __init__(self, client):
        self.bot = client

    async def on_voice_state_update(self, before, after):
        # VC user was before changing his state
        # None if he wasn't in VC before
        vc = before.voice.voice_channel

        # If user was in VC, we can edit this VC, there's no one in VC left and it was changed before
        if vc is not None and can_edit_channel(self.bot, vc) and len(vc.voice_members) == 0 and splittable(vc.name):
            await _reset_channel_name(self.bot, vc)
            logger.info("Removed language tag from {}".format(vc.name))

    # For logging only.
    @staticmethod
    async def on_command(self, ctx):
        msg = ctx.message
        logger.info('{}#{} sent \"{}\"'.format(msg.author.name, msg.author.discriminator, msg.content))

    async def on_command_error(self, exception, ctx):
        # Some of the imports are here because we only need them in this function
        from math import ceil
        from discord.ext.commands import CommandOnCooldown, CheckFailure, CommandNotFound

        # Actual code
        if isinstance(exception, CommandOnCooldown):
            seconds = exception.retry_after
            if seconds > 60:
                embed = error_embed(text_lines['mention']['slow_down_m'].format(ceil(seconds / 60)))
            else:
                embed = error_embed(text_lines['mention']['slow_down_s'].format(seconds))
            await self.bot.send_message(ctx.message.channel, embed=embed)
        elif isinstance(exception, CheckFailure):
            embed = error_embed(text_lines['mention']['no_access'])
            await self.bot.send_message(ctx.message.channel, embed=embed)
        elif isinstance(exception, CommandNotFound):
            pass
        else:
            embed = error_embed(text_lines['technical']['unknown_error'])
            print(exception)
            await self.bot.send_message(ctx.message.channel, embed=embed)


def setup(bot):
    bot.add_cog(Events(bot))
