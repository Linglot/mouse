import asyncio
import operator
from collections import OrderedDict

import more_itertools
from discord.ext import commands

from settings.config import settings
from settings.constants import MAIN_COLOR, ADMIN_ROLES, NATIVE_COLOR, YES_EMOJI, NO_EMOJI
from settings.lines import text_lines
from utils.utils import *


class RoleCommands:

    def __init__(self, bot):
        self.bot = bot

    # Command for role assigning.
    # It has multiple aliases which are adding either "native", "fluent", or "learning".
    # ;role alias is a normal one and can be used for any role basically.
    @commands.command(aliases=['role', 'native', 'fluent', 'learning', 'not'])
    @commands.guild_only()
    async def role_assign(self, ctx, *args):
        role_name = ' '.join(args).title()
        called_with = ctx.invoked_with

        if len(role_name.strip()) <= 0:
            await send_error_embed(ctx, (text_lines['roles']['assign']['empty']))
            return

        # We have to add some strings to make aliases searchable
        if called_with == 'native' or called_with == 'fluent' or called_with == 'learning':
            role_name = called_with.title() + ' ' + role_name

        splitted_name = role_name.split(' ')

        if splitted_name[0].lower() == 'native' or splitted_name[0].lower() == 'fluent':
            if await self.is_role_exist(ctx, splitted_name[1]):
                role_name = splitted_name[1]

        if not await self.is_role_exist(ctx, role_name):
            await send_error_embed(ctx, (text_lines['roles']['search']['no_role'].format(role_name.title())))
            return

        server = ctx.guild
        role = get_role(server, role_name)

        if not await self.is_role_assignable(role):
            await send_error_embed(ctx, (text_lines['roles']['assign']['not_allowed'].format(role.name.title())))
            return

        user = ctx.author

        # If a user has this role, we will remove it
        if role in user.roles:
            if role.color.value == NATIVE_COLOR and await self.will_become_nativeless(ctx):
                await send_error_embed(ctx, (text_lines['roles']['assign']['cant_remove_native']))
                return

            if called_with == 'not':
                await user.remove_roles(role, reason='self-removed')
            else:
                await self.role_yes_no_dialogue(ctx, role)
                return

            title = text_lines['roles']['assign']['removed'].format(role.name)

        # If a user doesn't have this role AND the command wasn't called with ;not alias we add a role
        elif called_with != 'not':
            # If a used doesn't have a native role we tell him to do that first
            if not await self.has_native_role(ctx) and role.color.value != NATIVE_COLOR:
                await send_error_embed(ctx, (text_lines['roles']['assign']['native_first']))
                return

            await user.add_roles(role, reason='self-added')
            title = text_lines['roles']['assign']['added'].format(role.name)

        # Basically an else for ;not command
        else:
            title = text_lines['roles']['assign']['dont_have']

        embed = discord.Embed(title=title, colour=discord.Colour(MAIN_COLOR))

        await ctx.send(embed=embed)

    # Command for searching users who have multiple tags
    # Syntax is: ;who role1[, role2 ...]
    @commands.command(aliases=['who', 'inrole', 'inroles'])
    @commands.guild_only()
    async def search(self, ctx, *args):
        searching_roles = self.make_role_list(args)

        if await self.multirole_checks(ctx, searching_roles):
            server = ctx.guild
            found_users = []
        else:
            return

        # Looking for peeps
        for member in server.members:
            user_roles = [str(role).lower() for role in member.roles]
            if set(searching_roles).issubset(user_roles):
                found_users.append(member)

        # If the result is 0 peeps, we have to show that
        number_of_results = len(found_users)
        if number_of_results == 0:
            no_results = discord.Embed(title=text_lines['roles']['search']['no_users_title'],
                                       description=text_lines['roles']['search']['try_again'],
                                       colour=discord.Colour(MAIN_COLOR))
            await ctx.send(embed=no_results)
            return

        # Making the title string ready
        if number_of_results == 1:
            title_line = ", ".join([role.title() for role in searching_roles])
            title = text_lines['roles']['search']['one_user'].format(title_line)
        else:
            title_line = ", ".join([role.title() for role in searching_roles])
            title = text_lines['roles']['search']['x_users'].format(number_of_results, title_line)

        embed = discord.Embed(title=title, colour=discord.Colour(MAIN_COLOR))

        # One column output
        if number_of_results < 6:
            if number_of_results == 1:
                header = text_lines['roles']['search']['one_user_header']
            else:
                header = text_lines['roles']['search']['many_users_header'].format(1, number_of_results)

            member_list = '\n'.join([member.display_name for member in found_users])
            embed.add_field(name=header, value=member_list, inline=True)
        # 3 columns output
        else:
            # if there's more than 30 users, we don't need to display the others
            # Also this is NOT(!) a changeable option due to discord limits
            if number_of_results > 30:
                found_users = [user for i, user in enumerate(found_users) if i < 30]
                excluded = number_of_results - 30
                embed.set_footer(text=text_lines['roles']['search']['and_more'].format(excluded))

            # Dividing roles by the 3 chunks, removing big names and making columns
            column_end_number = 0
            for chunk in enumerate(self.__create_chunks(found_users, 3)):
                # Bunch of useless variables, but it's better to use them
                # than count this stuff on the fly.
                old_cz = column_end_number + 1
                column_end_number += len(chunk[1])
                header = text_lines['roles']['search']['many_users_header'].format(old_cz, column_end_number)

                # Making a list with shorten names if needed
                member_list = '\n'.join([
                    self.shorten(member.display_name, settings['roles']['search']['max_length'])
                    for member in chunk[1]  # 1 cuz 0 is index
                ])
                embed.add_field(name=header, value=member_list, inline=True)

        await ctx.send(embed=embed)

    # Command for counting up users in following roles
    # Syntax is: ;count role1[, role2 ...]
    @commands.command()
    @commands.guild_only()
    async def count(self, ctx, *args):
        searching_roles = self.make_role_list(args)
        if await self.multirole_checks(ctx, searching_roles):
            server = ctx.guild
        else:
            return

        # String var we're going to fill now and use later.
        description_line = ""
        users_in_combination = 0

        # Counting the combination of peeps
        for member in server.members:
            user_roles = [str(role).lower() for role in member.roles]
            if set(searching_roles).issubset(user_roles):
                users_in_combination += 1

        # Looking for peeps
        for role in searching_roles:
            cur_res = 0
            for member in server.members:
                user_roles = [str(role).lower() for role in member.roles]
                if role in user_roles:
                    cur_res += 1

            # Forming a line for results
            description_line += text_lines['roles']['count']['total'].format(role.title(), cur_res)

        roles = ", ".join([role.title() for role in searching_roles])

        if users_in_combination <= 0:
            title = text_lines['roles']['count']['no_users'].format(roles)
        elif users_in_combination == 1:
            title = text_lines['roles']['count']['one_user'].format(roles)
        else:
            title = text_lines['roles']['count']['x_users'].format(users_in_combination, roles)

        if len(searching_roles) > 1:
            embed = discord.Embed(title=title,
                                  description=description_line,
                                  colour=discord.Colour(MAIN_COLOR))
        else:
            embed = discord.Embed(title=title,
                                  colour=discord.Colour(MAIN_COLOR))

        await ctx.send(embed=embed)

    # Command for pinging roles
    # Syntax is: ;ping native russian, learning english
    @commands.command(aliases=["mention"])
    @commands.has_any_role(*settings['roles']['ping']['allowed'])
    @commands.cooldown(rate=1, per=settings['roles']['ping']['cooldown'], type=commands.BucketType.user)
    @commands.guild_only()
    async def ping(self, ctx, *args):
        pinging_roles = self.make_role_list(args)
        if await self.multirole_checks(ctx, pinging_roles):
            server = ctx.guild
        else:
            return

        message = []
        gotta_change_later = []

        # You shouldn't be able to ping everyone and here
        for blacklist_item in settings['roles']['ping']['blacklist']:
            item = blacklist_item.lower()
            if item in pinging_roles:
                await send_error_embed(ctx, text_lines['roles']['ping']['cant_ping'].format(blacklist_item))
                return

        # Making some roles pingable and making a ping message
        for role in pinging_roles:
            current_role = get_role(server, role)
            if not current_role.mentionable:
                await current_role.edit(mentionable=True)
                gotta_change_later.append(role)
            message.append(current_role.mention)

        # Sending the ping message
        line = ", ".join(message)
        await ctx.send(content=line)

        # We gotta change back some of roles to unpingable
        for role in gotta_change_later:
            current_role = get_role(server, role)
            await current_role.edit(mentionable=False)

    # Top 10 roles command
    # This command is made exclusively for the Linglot server. Don't expect this working on other servers.
    # Syntax: ;top10
    @commands.command(aliases=['top'])
    @commands.guild_only()
    async def top10(self, ctx):
        server = ctx.message.guild

        roles = {role.name: len(role.members) for role in server.roles}

        native, fluent, learning = self.__make_top10_lines(roles)

        embed = discord.Embed(colour=discord.Colour(MAIN_COLOR))
        embed.set_author(name=server.name, icon_url=server.icon_url)

        embed.add_field(name="Natives", value=native, inline=True)
        embed.add_field(name="Fluent", value=fluent, inline=True)
        embed.add_field(name="Learning", value=learning, inline=True)

        embed.set_footer(text="Out of {} roles and {} members".format(len(roles), len(server.members)),
                         icon_url=self.bot.user.avatar_url)

        await ctx.send(embed=embed)

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

        # Too biggu nambaru?
        if x > settings['roles']['less_than']['limit']:
            await send_error_embed(ctx, (text_lines['roles']['less_than']['too_big']))
            return

        # Too sumarru nambaru?
        if x <= 0:
            await send_error_embed(ctx, (text_lines['roles']['less_than']['too_small']))
            return

        output = {role.name: len(role.members) for role in roles if len(role.members) < x}
        results = sorted(output.items(), reverse=True, key=operator.itemgetter(1))
        line = ', '.join([f"[{v}] {k}" for k, v in results])

        embed = discord.Embed(colour=discord.Colour(MAIN_COLOR),
                              title=text_lines['roles']['less_than']['title'].format(x),
                              description=line)

        await ctx.send(embed=embed)

    # Some helpful private functions

    # Basics check for commands if your want to check multiple roles
    async def multirole_checks(self, ctx, role_list) -> bool:
        if not await self.check_search_limit(role_list):
            await send_error_embed(ctx, (text_lines['roles']['search']['limit'].format(
                str(settings['roles']['search']['limit']))))
            return False

        if not await self.is_role_exist(ctx, role_list, output=True):
            return False

        return True

    # No or too many roles given equals "Bye"
    async def check_search_limit(self, role_list) -> bool:
        return 1 <= len(role_list) <= settings['roles']['search']['limit']

    # Do(es) certain role(s) even exist?
    async def is_role_exist(self, ctx, role_list, output=False) -> bool:
        server_roles = [role.name.lower() for role in ctx.guild.roles]

        # If we received a string in role_list then we gotta convert it to an array
        if isinstance(role_list, str):
            role_list = [role_list]  # (this is the worst code I ever wrote, gimme my java back)

        for role in role_list:
            if role.lower() not in server_roles:
                if output:
                    await send_error_embed(ctx, (text_lines['roles']['search']['no_role'].format(role)))
                return False

        return True

    # Returns true if role if self-assignable
    # If output = true it'll also send an error message
    async def is_role_assignable(self, role) -> bool:
        return role.color.value in settings['roles']['assign']['allowed_colors']

    # Returns true if user has AT LEAST ONE native role
    async def has_native_role(self, ctx):
        return any(role.color.value == NATIVE_COLOR for role in ctx.author.roles)

    # Returns true will have 0 native roles after removing one
    # If output = true it'll also send an error message
    async def will_become_nativeless(self, ctx):
        return len([role for role in ctx.author.roles if role.color.value == NATIVE_COLOR]) <= 1

    # Returns 3 strings of roles sorted from most the popular in chunks of 10
    def __make_top10_lines(self, roles):
        sorted_roles = sorted(roles.items(), reverse=True, key=operator.itemgetter(1))

        native, fluent, learning = {}, {}, {}
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

        def make_line(role_list) -> str:
            return '\n'.join([f"[{v}] {k}" for k, v in role_list.items()])

        return make_line(native), make_line(fluent), make_line(learning)

    async def role_yes_no_dialogue(self, ctx, role):
        embed = discord.Embed(title=text_lines['roles']['assign']['already_have_title'],
                              description=text_lines['roles']['assign']['already_have_msg'],
                              colour=discord.Colour(INFO_COLOR))
        msg = await ctx.send(embed=embed)
        await msg.add_reaction(YES_EMOJI)
        await msg.add_reaction(NO_EMOJI)

        def check(c_reaction, c_user):
            return c_reaction.message.id == msg.id and c_user == ctx.author

        try:
            reaction, user = await self.bot.wait_for('reaction_add',
                                                     timeout=settings['roles']['assign']['emoji_cd'],
                                                     check=check)
        except asyncio.TimeoutError:
            await msg.clear_reactions()
        else:
            if reaction.emoji == YES_EMOJI:
                await user.remove_roles(role, reason='self-removed')
                embed = discord.Embed(title=text_lines['roles']['assign']['removed'].format(role.name),
                                      colour=discord.Colour(MAIN_COLOR))
            else:
                embed = discord.Embed(title=text_lines['roles']['assign']['keep'].format(role.name),
                                      colour=discord.Colour(MAIN_COLOR))

            await msg.edit(embed=embed)
            await msg.clear_reactions()

    # Static methods

    # Divides list into N evenly-sized chunks
    @staticmethod
    def __create_chunks(list_to_divide, number_of_chunks):
        return [list(c) for c in more_itertools.divide(number_of_chunks, list_to_divide)]

    # Dividing roles to a list, removing unnecessary spaces and making it lowercase
    # "  native english,    fluent english " -> ["native english", "fluent english"]
    @staticmethod
    def make_role_list(role_string):
        result = [role.strip().lower() for role in " ".join(role_string).split(",") if role.strip() != ""]
        return list(OrderedDict.fromkeys(result))

    # Add a … symbol if the is longer than "limit"
    @staticmethod
    def shorten(string, limit) -> str:
        # "…" " " - 3 dots + 2x unbreakable spaces (alt+0160)
        return (string[:limit] + '…  ') if len(string) > limit else string


def setup(bot):
    bot.add_cog(RoleCommands(bot))
