from discord.ext import commands

from functions import *
from utils.tools import make_role_list


class ChatCommands:
    def __init__(self, bot):
        self.bot = bot

    # Command for changing VC's language in title
    # Syntax: ;lang Language Name
    @commands.command(aliases=["lang", "l"], pass_context=True)
    async def language(self, ctx, *args):
        user = ctx.message.author
        channel = ctx.message.channel
        vc = ctx.message.author.voice.voice_channel

        # Since we get out name as an array of strings, we should connect 'em
        # ["lol","qwe"] -> "lol qwe"
        lang_name = " ".join(args)

        await voice.change_vc_name(self.bot, user, channel, vc, lang_name)

    # Command for removing language name from VC's name
    # Syntax: ;resetlang
    @commands.command(aliases=["rl"], pass_context=True)
    async def resetlang(self, ctx):
        user = ctx.message.author
        channel = ctx.message.channel
        vc = ctx.message.author.voice.voice_channel

        await voice.reset_vc_name(self.bot, user, channel, vc)

    # Command for searching users who have multiple tags
    # Syntax is: ;who role1[, role2 ...]
    @commands.command(aliases=["inroles"], pass_context=True)
    async def who(self, ctx, *args):
        server = ctx.message.server
        channel = ctx.message.channel
        searching_roles = make_role_list(args)

        await roles.role_search(self.bot, server, channel, searching_roles)


# Simple bot-info command
# Shows discord invite link, git, and some bot-related info
# Syntax: ;about
@commands.command(aliases=["info"], pass_context=True)
async def about(self, ctx):
    await info.show_about(self.bot, ctx.message.channel)


# Version command
# Syntax: ;version
@commands.command(aliases=["ver"], pass_context=True)
async def version(self, ctx):
    await info.show_version(self.bot, ctx.message.channel)


def setup(bot):
    bot.add_cog(ChatCommands(bot))
