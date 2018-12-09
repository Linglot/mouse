from _config import *
from discord.ext import commands
from _lines import text_lines
from utils import *


class About:
    def __init__(self, bot):
        self.bot = bot

    # Simple bot-info command
    # Shows discord invite link, git, and some bot-related info
    # Syntax: ;about
    @commands.command(aliases=["about", "info"], pass_context=True)
    async def show_info(self, ctx):
        # Creating table
        embed = discord.Embed(colour=discord.Colour(OFF_COLOR_3),
                              description=text_lines['about']['about_desc'])

        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_author(name=self.bot.user.name)
        embed.set_footer(text=text_lines['version']['version_currently'].format(CURRENT_VERSION))

        embed.add_field(name=text_lines['about']['about_gh_link'], value=text_lines['about']['about_gh_desc'],
                        inline=True)
        embed.add_field(name=text_lines['about']['about_inv_link'], value=text_lines['about']['about_inv_desc'],
                        inline=True)

        await self.bot.send_message(ctx.message.channel, embed=embed)


def setup(bot):
    bot.add_cog(About(bot))
