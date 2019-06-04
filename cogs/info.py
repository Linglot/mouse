import operator

from discord import TextChannel, VoiceChannel
from discord.ext import commands

from settings.constants import CURRENT_VERSION, GITHUB_LINK, NATIVE_COLOR, FLUENT_COLOR, LEARNING_COLOR, MAIN_COLOR
from settings.lines import text_lines
from utils.utils import *


# This class is designed to have commands that are somehow related to getting general information about stuff
class InfoCommands:
    def __init__(self, bot):
        self.bot = bot

    # Top 10 roles command
    # This command is made exclusively for the Linglot server. Don't expect this working on other servers.
    # Syntax: ;top10, ;top
    @commands.command(aliases=['top'])
    @commands.guild_only()
    async def top10(self, ctx):
        server = ctx.message.guild

        roles = {role.name: len(role.members) for role in server.roles}

        # Making 3 dictionaries with 10 roles in each
        native, fluent, learning = self.__make_top10_lines(roles)

        # Preparing embed
        embed = discord.Embed(colour=discord.Colour(MAIN_COLOR))
        embed.set_author(name=server.name, icon_url=server.icon_url)

        embed.add_field(name="Natives", value=native, inline=True)
        embed.add_field(name="Fluent", value=fluent, inline=True)
        embed.add_field(name="Learning", value=learning, inline=True)

        embed.set_footer(text=text_lines['roles']['top10']['bottom_line'].format(len(roles), len(server.members)),
                         icon_url=self.bot.user.avatar_url)

        await ctx.send(embed=embed)

    # Server info command. Shows as much as it can.
    # Syntax: ;serverinfo, ;server, ;si
    @commands.command(name='serverinfo', aliases=['server', 'si'])
    @commands.guild_only()
    async def server_info(self, ctx):
        server = ctx.message.guild

        # Getting the amount of language roles
        language_roles = len([role for role in server.roles if
                              role.color.value == NATIVE_COLOR or
                              role.color.value == FLUENT_COLOR or
                              role.color.value == LEARNING_COLOR])

        # Getting the amount of "white" users
        without_roles = len([member for member in server.members if len(member.roles) == 1])

        # Initializing vars for the amount of text and voice channels
        text = 0
        vc = 0

        # All the calculations and stuff
        v_owner = get_full_name(server.owner)
        v_roles = text_lines['server_info']['roles'].format(language_roles, len(server.roles) - language_roles)

        # Yata said we don't need features, so.
        # v_features = ", ".join(server.features) if len(server.features) > 0 else text_lines['technical']['none']

        v_default_channel = server.system_channel.mention if server.system_channel else text_lines['technical']['none']
        v_created_at = server.created_at.strftime("%H:%M:%S at %d %b %Y")
        v_members_total = len(server.members)
        v_members = text_lines['server_info']['members_line'].format(v_members_total - without_roles, without_roles)
        v_emoji_total = len(server.emojis)
        v_emoji = "".join([str(emoji) for emoji in server.emojis])

        # Counting the amount of VCs and Text channels
        for server_channel in server.channels:
            if isinstance(server_channel, TextChannel):
                text += 1
            elif isinstance(server_channel, VoiceChannel):
                vc += 1
        v_channels_total = text + vc
        v_channels = text_lines['server_info']['channel_line'].format(text, vc)

        # Preparing embed
        embed = discord.Embed(colour=discord.Colour(INFO_COLOR))
        embed.set_thumbnail(url=server.icon_url)
        embed.set_author(name=server.name, icon_url=server.icon_url)

        embed.add_field(name=text_lines['server_info']['titles']['id'],
                        value=server.id,
                        inline=True)
        embed.add_field(name=text_lines['server_info']['titles']['owner'],
                        value=v_owner,
                        inline=True)
        embed.add_field(name=text_lines['server_info']['titles']['created_at'],
                        value=v_created_at,
                        inline=True)
        embed.add_field(name=text_lines['server_info']['titles']['region'],
                        value=server.region,
                        inline=True)
        embed.add_field(name=text_lines['server_info']['titles']['channels'].format(v_channels_total),
                        value=v_channels,
                        inline=True)
        embed.add_field(name=text_lines['server_info']['titles']['default_channel'],
                        value=v_default_channel,
                        inline=True)
        embed.add_field(name=text_lines['server_info']['titles']['roles'].format(len(server.roles)),
                        value=v_roles,
                        inline=True)
        embed.add_field(name=text_lines['server_info']['titles']['members'].format(v_members_total),
                        value=v_members,
                        inline=True)

        # Features block, if needed
        # embed.add_field(name=text_lines['server_info']['titles']['features'],
        #                 value=v_features,
        #                 inline=True)

        # Otherwise it will crash because there's a 1024 symbols limit per 1 table block and emoji's line isn't 1 synbol per emoji
        # but their "shortcuts" like ":uta::mishmish::ghosthug:" etc which could get really big.
        # Technically could be rewritten by dividing it into several blocks
        if len(v_emoji) <= 1024:
            embed.add_field(name=text_lines['server_info']['titles']['emojis'].format(v_emoji_total),
                            value=v_emoji,
                            inline=False)

        await ctx.send(embed=embed)

    # Simple bot-info command
    # Shows discord invite link, git, and some bot-related info
    # Syntax: ;about, ;botinfo
    @commands.command(name='about', aliases=['botinfo'])
    async def show_about(self, ctx):
        # Preparing embed
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

    # Shows the version in a simple embed
    # Syntax: ;version
    @commands.command(name='version', aliases=['ver'])
    async def show_version(self, ctx):
        # Preparing embed
        embed = discord.Embed(title=text_lines['version']['version_currently'].format(CURRENT_VERSION),
                              colour=discord.Colour(INFO_COLOR))
        embed.set_footer(text=text_lines['version']['version_footer'].format(self.bot.user.name),
                         icon_url=self.bot.user.avatar_url)

        await ctx.send(embed=embed)

    # Shows the github link
    # Syntax: ;github. ;git
    @commands.command(aliases=['git'])
    async def github(self, ctx):
        # Creating table
        embed = discord.Embed(title=text_lines['github']['github'],
                              description=GITHUB_LINK,
                              colour=discord.Colour(INFO_COLOR))
        embed.set_footer(text=text_lines['version']['version_footer'].format(self.bot.user.name),
                         icon_url=self.bot.user.avatar_url)

        await ctx.send(embed=embed)

    # Tech command for ;top10
    # Returns 3 strings of roles sorted from most the popular in chunks of 10
    def __make_top10_lines(self, roles):
        sorted_roles = sorted(roles.items(), reverse=True, key=operator.itemgetter(1))

        native, fluent, learning = {}, {}, {}
        # Basically goes through each role, looking up their color and placing it in one of the "blocks"
        # If the block is full (10 roles) just skip it.
        # Return the loop if all the block are full
        for key, value in sorted_roles:
            role_name = key.split()
            if role_name[0] == "Native" and len(native) < 10:
                native[role_name[1]] = value
            if role_name[0] == "Fluent" and len(fluent) < 10:
                fluent[role_name[1]] = value
            if role_name[0] == "Learning" and len(learning) < 10 and role_name[1].lower() != 'other':
                learning[role_name[1]] = value

            if native == fluent == learning == 10:
                break

        # Makes a new line character after each role so it would look nicer
        def make_line(role_list) -> str:
            return '\n'.join([f"[{v}] {k}" for k, v in role_list.items()])

        return make_line(native), make_line(fluent), make_line(learning)


def setup(bot):
    bot.add_cog(InfoCommands(bot))
