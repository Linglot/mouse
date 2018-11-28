import discord
from _config import *
from discord.ext import commands
from _lines import *
from utils import *
import random


class ChatCommands:
    def __init__(self, bot):
        self.bot = bot

    # Command for changing VC's language in title
    # Syntax: ;lang Language Name
    @commands.command(aliases=["lang", "l"], pass_context=True)
    async def change_channel_lang(self, ctx, *args):

        # If user isn't even in VC
        if ctx.message.author is None or ctx.message.author.voice.voice_channel is None:
            await self.bot.send_message(ctx.message.channel, lang_must_be_in_vc)
            return

        vc = ctx.message.author.voice.voice_channel

        # Permissions check
        if not can_edit_channel(self.bot, vc):
            await self.bot.send_message(ctx.message.channel, lang_cant_edit)
            return

        # Since we get out name as an array of strings, we should connect 'em
        # ["lol","qwe"] -> "lol qwe"
        lang_name = " ".join(args)

        # Empty? Pass
        if len(lang_name.strip()) == 0:
            await self.bot.send_message(ctx.message.channel, random.choice(lang_if_nothing))
            return

        # If we get "reset" then we're going to use another function
        if lang_name.strip() == "reset":
            await self.reset_lang.callback(self, ctx)
            return

        # I wish my iq were that big (20 chars max length)
        if len(lang_name) > settings['change_channel_lang']['max_lang_name_length']:
            await self.bot.send_message(ctx.message.channel, lang_make_shorter)
            return

        # If the name could be split (or had been changed in the past, in other words)
        # when we just need to change the last part
        if splittable(vc.name):
            # This is poop code right there, TODO: rewrite
            await self.bot.edit_channel(vc, name="{} {} {}".format(get_original_name(vc.name), VOICE_CHANNEL_DIVIDER,
                                                                   lang_name))
        # Otherwise add a suffix
        else:
            await self.bot.edit_channel(vc, name="{} {} {}".format(vc.name, VOICE_CHANNEL_DIVIDER, lang_name))
        await self.bot.send_message(ctx.message.channel, lang_were_set.format(lang_name))

    # TODO: Remove code duplication with VC behaviour's function
    # Command for removing language name from VC's name
    # Syntax: ;resetlang
    @commands.command(aliases=["resetlang", "rl"], pass_context=True)
    async def reset_lang(self, ctx):
        if ctx.message.author is None or ctx.message.author.voice.voice_channel is None:
            await self.bot.send_message(ctx.message.channel, lang_must_be_in_vc)
            return

        vc = ctx.message.author.voice.voice_channel
        oc_name = get_original_name(vc.name)

        # If we can't edit channel, then we can't reset its name
        if can_edit_channel(self.bot, vc):
            await self.bot.edit_channel(vc, name=oc_name)
            await self.bot.send_message(ctx.message.channel, lang_were_reset.format(oc_name))
        else:
            await self.bot.send_message(ctx.message.channel, lang_cant_edit)

    # Command for searching users who have multiple tags
    # Syntax is: lang
    @commands.command(aliases=["who", "inroles"], pass_context=True)
    async def combine_search(self, ctx, *args):
        server = ctx.message.server
        found_users = []

        # Dividing roles to a list, removing unnecessary spaces and making it lowercase
        searching_roles = [role.strip().lower() for role in " ".join(args).split(",") if role.strip() != ""]

        # You can use use nadeko's .inrole, if you want to get 1 role only
        if len(searching_roles) < 2 or len(searching_roles) > settings['combined_search']['role_limit']:
            embed_error = discord.Embed(
                description=text_lines['combined_search']['min_max_roles_amount'].format(
                    str(settings['combined_search']['role_limit'])),
                colour=discord.Colour(SECONDARY_COLOR))

            await self.bot.send_message(ctx.message.channel, embed=embed_error)
            return

        # Do these roles even exist?
        server_roles = [role.name.lower() for role in server.roles]
        for role in searching_roles:
            # If at least one doesn't = rip
            if not role in server_roles:
                embed_error = discord.Embed(
                    description=text_lines['combined_search']['no_such_role'].format(role.title()),
                    colour=discord.Colour(SECONDARY_COLOR))

                await self.bot.send_message(ctx.message.channel, embed=embed_error)
                return

        # Looking for peeps
        for member in server.members:
            user_roles = [str(role).lower() for role in member.roles]
            if set(searching_roles).issubset(user_roles):
                found_users.append(member)

        # If the result is 0 peeps, we have to show that
        number_of_results = len(found_users)
        if number_of_results == 0:
            embed_error = discord.Embed(title=text_lines['combined_search']['no_users_found'],
                                        description=text_lines['combined_search']['try_another_one'],
                                        colour=discord.Colour(MAIN_COLOR))

            await self.bot.send_message(ctx.message.channel, embed=embed_error)
            return

        # Making the title string ready
        title = text_lines['combined_search']['users_for'].format(
            ", ".join([role.title() for role in searching_roles]))

        embed = discord.Embed(title=title, colour=discord.Colour(MAIN_COLOR))

        # Grabbing the lines
        lines = [
            text_lines['combined_search']['row_1_column'],
            str(number_of_results),  # Just the number
            text_lines['combined_search']['row_3_column']
        ]

        if number_of_results < 6:
            embed.add_field(name=text_lines['combined_search']['row_1_column_only'],
                            value='\n'.join([member.display_name for member in found_users]),
                            inline=True)
        else:
            # if there's more than 30 users, we don't need to display the others
            # Also this is NOT(!) a changeable option due to discord limits
            if number_of_results > 30:
                found_users = [user for i, user in enumerate(found_users) if i < 10 * 3]
                excluded = number_of_results - 30
                embed.set_footer(text=text_lines['combined_search']['and_many_more'].format(excluded))

            # Dividing roles by the 3 chunks, removing big names and making columns
            for i, chunk in enumerate(create_chunks(found_users, 3)):
                row_users_list = [
                    add_dots(member.display_name, settings['combined_search']['max_user_name_length'])
                    for member in chunk
                ]
                embed.add_field(name=lines[i], value='\n'.join(row_users_list), inline=True)

        await self.bot.send_message(ctx.message.channel, embed=embed)

    # Simple bot-info command
    # Shows discord invite link, git, and some bot-related info
    # Syntax: ;about
    @commands.command(aliases=["about", "info"], pass_context=True)
    async def show_info(self, ctx):

        # Creating table
        embed = discord.Embed(colour=discord.Colour(OFF_COLOR_3),
                              description=about_desc)

        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_author(name=self.bot.user.name)
        embed.set_footer(text=version_currently.format(CURRENT_VERSION))

        embed.add_field(name=about_gh_link, value=about_gh_desc, inline=True)
        embed.add_field(name=about_inv_link, value=about_inv_desc, inline=True)

        await self.bot.send_message(ctx.message.channel, embed=embed)

    # Version command
    # Syntax: ;version
    @commands.command(aliases=["version", "ver"], pass_context=True)
    async def show_version(self, ctx):

        # Creating table
        embed = discord.Embed(title=version_currently.format(CURRENT_VERSION),
                              colour=discord.Colour(OFF_COLOR_3))
        embed.set_footer(text=version_footer.format(self.bot.user.name), icon_url=self.bot.user.avatar_url)

        await self.bot.send_message(ctx.message.channel, embed=embed)


def setup(bot):
    bot.add_cog(ChatCommands(bot))
