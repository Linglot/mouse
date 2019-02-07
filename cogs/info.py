import operator

from discord import TextChannel, VoiceChannel
from discord.ext import commands

from settings.constants import CURRENT_VERSION, GITHUB_LINK, MAIN_COLOR
from settings.lines import text_lines
from utils.tools import *


class InfoCommands:

    def __init__(self, bot):
        self.bot = bot

    # Top 10 roles command
    # This command is made exclusively for the Linglot server. Don't expect this working on other servers.
    # Syntax: ;top10
    # TODO: DO A REFACTOR AND MOVE TO ROLES.PY
    @commands.command(aliases=['top'])
    @commands.guild_only()
    async def top10(self, ctx):
        server = ctx.message.guild

        role_dict = {}
        for role in server.roles:
            role_dict[role.name] = len(role.members)
        roles_sorted = sorted(role_dict.items(), reverse=True, key=operator.itemgetter(1))

        native = {}
        fluent = {}
        learning = {}

        for key, value in roles_sorted:
            role_name = key.split()
            if role_name[0] == "Native":
                if len(native) < 10:
                    native[role_name[1]] = value
            if role_name[0] == "Fluent":
                if len(fluent) < 10:
                    fluent[role_name[1]] = value
            if role_name[0] == "Learning":
                if len(learning) < 10:
                    learning[role_name[1]] = value

            if native == fluent == learning == 10:
                break

        embed = discord.Embed(colour=discord.Colour(MAIN_COLOR))
        embed.set_author(name=server.name, icon_url=server.icon_url)

        print(native)

        embed.add_field(name="Natives",
                        value="\n".join([f"[{v}] {k}" for k, v in native.items()]),
                        inline=True)
        embed.add_field(name="Fluent",
                        value="\n".join([f"[{v}] {k}" for k, v in fluent.items()]),
                        inline=True)
        embed.add_field(name="Learning",
                        value="\n".join([f"[{v}] {k}" for k, v in learning.items()]),
                        inline=True)

        embed.set_footer(text="Out of {} roles and {} members".format(len(role_dict), len(server.members)),
                         icon_url=self.bot.user.avatar_url)

        await ctx.send(embed=embed)

    # Server info command. Shows as much as it can.
    # Syntax: ;serverinfo
    @commands.command(name='serverinfo', aliases=['server', 'si'])
    @commands.guild_only()
    async def server_info(self, ctx):
        server = ctx.message.guild
        without_roles = len([member for member in server.members if len(member.roles) == 1])
        text = 0
        vc = 0

        v_owner = name(server.owner)
        v_roles = text_lines['server_info']['x_roles'].format(len(server.roles))
        v_features = ", ".join(server.features) if len(server.features) > 0 else text_lines['technical']['none']
        v_default_channel = server.system_channel.mention if server.system_channel else text_lines['technical']['none']
        v_created_at = server.created_at.strftime("%H:%M at %d %b %Y")
        v_members = text_lines['server_info']['members_line'].format(len(server.members), without_roles)
        v_emoji = ", ".join([str(emoji) for emoji in server.emojis])

        for server_channel in server.channels:
            if isinstance(server_channel, TextChannel):
                text += 1
            elif isinstance(server_channel, VoiceChannel):
                vc += 1
        v_channels = text_lines['server_info']['channel_line'].format(text, vc)

        # Creating table
        embed = discord.Embed(colour=discord.Colour(INFO_COLOR))
        embed.set_thumbnail(url=server.icon_url)
        embed.set_author(name=server.name, icon_url=server.icon_url)

        embed.add_field(name=text_lines['server_info']['titles']['id'],
                        value=server.id,
                        inline=True)
        embed.add_field(name=text_lines['server_info']['titles']['owner'],
                        value=v_owner,
                        inline=True)
        embed.add_field(name=text_lines['server_info']['titles']['region'],
                        value=server.region,
                        inline=True)
        embed.add_field(name=text_lines['server_info']['titles']['roles'],
                        value=v_roles,
                        inline=True)
        embed.add_field(name=text_lines['server_info']['titles']['features'],
                        value=v_features,
                        inline=True)
        embed.add_field(name=text_lines['server_info']['titles']['default_channel'],
                        value=v_default_channel,
                        inline=True)
        embed.add_field(name=text_lines['server_info']['titles']['channels'],
                        value=v_channels,
                        inline=True)
        embed.add_field(name=text_lines['server_info']['titles']['created_at'],
                        value=v_created_at,
                        inline=True)
        embed.add_field(name=text_lines['server_info']['titles']['members'],
                        value=v_members,
                        inline=True)

        # Otherwise it will crash
        if len(v_emoji) <= 1024:
            embed.add_field(name=text_lines['server_info']['titles']['emojis'], value=v_emoji, inline=False)

        await ctx.send(embed=embed)

    # Simple bot-info command
    # Shows discord invite link, git, and some bot-related info
    # Syntax: ;about
    @commands.command(name='about', aliases=['info'])
    async def show_about(self, ctx):
        # Creating table
        embed = discord.Embed(colour=discord.Colour(INFO_COLOR),
                              description=text_lines['about']['about_desc'])

        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_author(name=self.bot.user.name)
        embed.set_footer(text=text_lines['version']['version_currently'].format(CURRENT_VERSION))

        embed.add_field(name=text_lines['about']['about_gh_link'], value=text_lines['about']['about_gh_desc'],
                        inline=True)
        embed.add_field(name=text_lines['about']['about_inv_link'], value=text_lines['about']['about_inv_desc'],
                        inline=True)

        await ctx.send(embed=embed)

    # Version command
    # Syntax: ;version
    @commands.command(name='version', aliases=['ver'])
    async def show_version(self, ctx):
        # Creating table
        embed = discord.Embed(title=text_lines['version']['version_currently'].format(CURRENT_VERSION),
                              colour=discord.Colour(INFO_COLOR))
        embed.set_footer(text=text_lines['version']['version_footer'].format(self.bot.user.name),
                         icon_url=self.bot.user.avatar_url)

        await ctx.send(embed=embed)

    # Github command
    # Syntax: ;github
    @commands.command(aliases=['git'])
    async def github(self, ctx):
        # Creating table
        embed = discord.Embed(title=text_lines['github']['github'],
                              description=GITHUB_LINK,
                              colour=discord.Colour(INFO_COLOR))
        embed.set_footer(text=text_lines['version']['version_footer'].format(self.bot.user.name),
                         icon_url=self.bot.user.avatar_url)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(InfoCommands(bot))
