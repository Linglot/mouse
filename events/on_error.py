from discord import Forbidden
from discord.ext.commands import CheckFailure, NoPrivateMessage, CommandNotFound, Cog

from settings.lines import text_lines
from utils.utils import send_error_embed


class OnError(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_command_error(self, ctx, exception):
        channel = ctx.channel

        if isinstance(exception, NoPrivateMessage):
            await send_error_embed(ctx, text_lines['technical']['cant_do_in_pm'])
        elif isinstance(exception, CheckFailure):
            await send_error_embed(ctx, text_lines['roles']['ping']['no_access'])
        elif isinstance(exception, CommandNotFound):
            return
        elif isinstance(exception, Forbidden):
            await send_error_embed(ctx, text_lines['technical']['forbidden'].format(channel.name, ctx.guild), dm=True)
        else:
            await send_error_embed(ctx, text_lines['technical']['unknown_error'].format(exception))


def setup(bot):
    bot.add_cog(OnError(bot))
