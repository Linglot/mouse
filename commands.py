from discord.ext import commands

from functions import *


class ChatCommands:
    def __init__(self, bot):
        self.bot = bot

    # Command for changing VC's language in title
    # Syntax: ;lang Language Name
    @commands.command(aliases=["lang", "l"], pass_context=True)
    async def language(self, ctx, *args):
        await voice.change_vc_name(self.bot, ctx, args)

    # TODO: Remove code duplication with VC behaviour's function
    # Command for removing language name from VC's name
    # Syntax: ;resetlang
    @commands.command(aliases=["resetlang", "rl"], pass_context=True)
    async def resetlang(self, ctx):
        await voice.reset_vc_name(self.bot, ctx)

    # Command for searching users who have multiple tags
    # Syntax is: lang
    @commands.command(aliases=["who", "inroles"], pass_context=True)
    async def combine_search(self, ctx, *args):
        await combine_search.combine_search(self.bot, ctx, args)

    # Simple bot-info command
    # Shows discord invite link, git, and some bot-related info
    # Syntax: ;about
    @commands.command(aliases=["about", "info"], pass_context=True)
    async def show_info(self, ctx):
        await about.show_info(self.bot, ctx)

    # Version command
    # Syntax: ;version
    @commands.command(aliases=["version", "ver"], pass_context=True)
    async def show_version(self, ctx):
        await version.show_version(self.bot, ctx)


def setup(bot):
    bot.add_cog(ChatCommands(bot))