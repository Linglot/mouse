import discord
from discord.ext import commands

from _config import CURRENT_VERSION, OFF_COLOR_3
from _lines import text_lines


class Version:
    def __init__(self, bot):
        self.bot = bot

    # Version command
    # Syntax: ;version
    @commands.command(aliases=["version", "ver"], pass_context=True)
    async def show_version(self, ctx):
        # Creating table
        embed = discord.Embed(title=text_lines['version']['version_currently'].format(CURRENT_VERSION),
                              colour=discord.Colour(OFF_COLOR_3))
        embed.set_footer(text=text_lines['version']['version_footer'].format(self.bot.user.name),
                         icon_url=self.bot.user.avatar_url)

        await self.bot.send_message(ctx.message.channel, embed=embed)


def setup(bot):
    bot.add_cog(Version(bot))
