import operator

import discord
from discord.ext import commands

from settings.config import settings
from settings.constants import ADMIN_ROLES, MAIN_COLOR
from settings.lines import text_lines
from utils.utils import send_error_embed


# This class is mainly designed for having admin-only commands in it, whether of their functionality
class AdminCommands:
    def __init__(self, bot):
        self.bot = bot

    # Searches for roles with less than X members
    # Syntax: ;lessthan 10
    @commands.command(aliases=["lessthan", "less"])
    @commands.has_any_role(*ADMIN_ROLES)
    @commands.guild_only()
    async def less_than(self, ctx, *args):
        roles = ctx.guild.roles
        try:
            x = int("".join(args))
        except:
            await send_error_embed(ctx, (text_lines['roles']['less_than']['not_number']))
            return

        # If the number is too big we're sending an error
        if x > settings['roles']['less_than']['limit']:
            await send_error_embed(ctx, (text_lines['roles']['less_than']['too_big']))
            return

        # If the number is too small we're sending an error
        if x <= 0:
            await send_error_embed(ctx, (text_lines['roles']['less_than']['too_small']))
            return

        # Preparing results for outputting
        output = {role.name: len(role.members) for role in roles if len(role.members) < x}
        results = sorted(output.items(), reverse=True, key=operator.itemgetter(1))
        line = ', '.join([f"[{v}] {k}" for k, v in results])

        #Preparing embed for outputting
        embed = discord.Embed(colour=discord.Colour(MAIN_COLOR),
                              title=text_lines['roles']['less_than']['title'].format(x),
                              description=line)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(AdminCommands(bot))
