from discord.ext import commands

from cogs import *
from settings.config import settings
from utils.utils import make_role_list


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
        lang_name = " ".join(args).title()

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
    @commands.command(aliases=["inrole", "inroles"], pass_context=True)
    async def who(self, ctx, *args):
        server = ctx.message.server
        channel = ctx.message.channel
        searching_roles = make_role_list(args)

        await roles.role_search(self.bot, server, channel, searching_roles)

    # Command for counting up users in following roles
    # Syntax is: ;count role1[, role2 ...]
    @commands.command(pass_context=True)
    async def count(self, ctx, *args):
        server = ctx.message.server
        channel = ctx.message.channel
        searching_roles = make_role_list(args)

        await roles.role_count(self.bot, server, channel, searching_roles)

    # Command for pinging roles
    # Syntax is: ;ping
    @commands.command(aliases=["mention"], pass_context=True)
    @commands.has_any_role(*settings['ping']['roles_allowed_to_ping'])
    @commands.cooldown(rate=1, per=settings['ping']['cooldown'], type=commands.BucketType.user)
    async def ping(self, ctx, *args):
        server = ctx.message.server
        channel = ctx.message.channel
        pinging_roles = make_role_list(args)

        await roles.ping(self.bot, server, channel, pinging_roles)
