from math import ceil

from discord import Forbidden
from discord.ext.commands import CommandOnCooldown, CheckFailure, NoPrivateMessage, CommandNotFound

from settings.lines import text_lines
from utils.tools import error_embed


class OnError:
    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, exception):
        channel = ctx.channel

        if isinstance(exception, CommandOnCooldown):
            seconds = exception.retry_after
            if seconds > 60:
                embed = error_embed(text_lines['mention']['slow_down_m'].format(ceil(seconds / 60)))
            else:
                embed = error_embed(text_lines['mention']['slow_down_s'].format(seconds))
            await ctx.send(embed=embed)
        elif isinstance(exception, NoPrivateMessage):
            embed = error_embed(text_lines['technical']['cant_do_in_pm'])
            await ctx.send(embed=embed)
        elif isinstance(exception, CheckFailure):
            embed = error_embed(text_lines['mention']['no_access'])
            await ctx.send(embed=embed)
        elif isinstance(exception, CommandNotFound):
            return
        elif isinstance(exception, Forbidden):
            embed = error_embed(text_lines['technical']['forbidden'].format(channel.name, ctx.guild))
            await ctx.author.dm_channel.send(embed=embed)
        else:
            embed = error_embed(text_lines['technical']['unknown_error'].format(exception))
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(OnError(bot))