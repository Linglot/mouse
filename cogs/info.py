from discord import TextChannel, VoiceChannel
from discord.ext import commands

import discord

from settings.constants import CURRENT_VERSION, GITHUB_LINK, LANGUAGE_ROLES, INFO_COLOR
from settings.lines import text_lines


class InfoCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Server info command. Shows as much as it can.
    # Syntax: ;serverinfo
    @commands.command(name='serverinfo', aliases=['server', 'si'])
    @commands.guild_only()
    async def server_info(self, ctx):
        server = ctx.message.guild

        # Get number of language roles on the server
        language_role_count = len(list(filter(lambda role: role in LANGUAGE_ROLES, server.roles)))

        # Get number of users without any roles on the server
        # Every user is implicitly in `@everyone`, which is why we check if `len(member.roles) == 1`
        roleless_user_count = len(list(filter(lambda member: len(member.roles) == 1, server.members)))

        role_info = text_lines['server_info']['roles'].format(language_role_count,
                                                              len(server.roles) - language_role_count)

        # TODO: Determine if guilds can be without a default channel
        default_channel = server.system_channel.mention if server.system_channel else text_lines['technical']['none']

        total_members = len(server.members)
        member_info = text_lines['server_info']['members_line'].format(total_members - roleless_user_count,
                                                                       roleless_user_count)

        emoji_count = len(server.emojis)
        # This is a string of *all* custom emojis in the server
        emoji_preview = "".join([str(emoji) for emoji in server.emojis])

        # Counts the number of text and voice channels in the server
        text_channel_count = len(list(filter(lambda channel: isinstance(channel, TextChannel), server.channels)))
        voice_channel_count = len(server.channels) - text_channel_count
        channel_info = text_lines['server_info']['channel_line'].format(text_channel_count, voice_channel_count)

        # Create table for server info
        embed = discord.Embed(colour=discord.Colour(INFO_COLOR))
        embed.set_thumbnail(url=server.icon_url)
        embed.set_author(name=server.name, icon_url=server.icon_url)
        embed.add_field(name=text_lines['server_info']['titles']['id'],
                        value=server.id,
                        inline=True)
        embed.add_field(name=text_lines['server_info']['titles']['owner'],
                        value=server.owner,
                        inline=True)
        embed.add_field(name=text_lines['server_info']['titles']['created_at'],
                        value=server.created_at.strftime("%H:%M:%S at %d %b %Y"),
                        inline=True)
        embed.add_field(name=text_lines['server_info']['titles']['region'],
                        value=server.region,
                        inline=True)
        embed.add_field(name=text_lines['server_info']['titles']['channels'].format(len(server.channels)),
                        value=channel_info,
                        inline=True)
        embed.add_field(name=text_lines['server_info']['titles']['default_channel'],
                        value=default_channel,
                        inline=True)
        embed.add_field(name=text_lines['server_info']['titles']['roles'].format(len(server.roles)),
                        value=role_info,
                        inline=True)
        embed.add_field(name=text_lines['server_info']['titles']['members'].format(total_members),
                        value=member_info,
                        inline=True)

        # The max length for content in an embed is 1024 characters, and the minimum length is 1 character
        # If the emoji preview string is empty, or greater than 1024 characters, discord will reject our content
        # So, we only show emoji information if the preview string is within those bounds
        if 0 < len(emoji_preview) <= 1024:
            embed.add_field(name=text_lines['server_info']['titles']['emojis'].format(emoji_count),
                            value=emoji_preview,
                            inline=False)

        await ctx.send(embed=embed)

    # Simple bot-info command
    # Shows discord invite link, git, and some bot-related info
    # Syntax: ;about
    @commands.command(name='about', aliases=['botinfo'])
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
