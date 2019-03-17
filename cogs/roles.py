import operator
from collections import OrderedDict

import more_itertools
from discord.ext import commands

from settings.config import settings
from settings.constants import MAIN_COLOR, ADMIN_ROLES, NATIVE_COLOR
from settings.lines import text_lines
from utils.utils import *


class RoleCommands:

    def __init__(self, bot):
        self.bot = bot

    # Command for role assigning.
    # It has multiple aliases which are adding either "native", "fluent", or "learning".
    # ;role alias is a normal one and can be used for any role basically.
    @commands.command(aliases=['role', 'native', 'fluent', 'learning'])
    @commands.guild_only()
    async def role_assign(self, ctx, *args):
        if ctx.invoked_with == 'native':
            role_name = 'Native ' + ' '.join(args).title()
        elif ctx.invoked_with == 'fluent':
            role_name = 'Fluent ' + ' '.join(args).title()
        elif ctx.invoked_with == 'learning':
            role_name = 'Learning ' + ' '.join(args).title()
        else:
            role_name = ' '.join(args).title()

        splitted = role_name.split(' ')

        if not await self.__check_if_role_exists(ctx, role_name) and (
                splitted[0] == 'native' or splitted[0] == 'fluent'):
            # if we can't find it normal way let's try to look up for low-population roles.
            if await self.__check_if_role_exists(ctx, splitted[1]):
                # If found we gotta change our role name
                role_name = splitted[1]
            else:
                return False

        server = ctx.guild
        role = get_role(server, role_name)

        if not await self.__check_allowability_of_role(ctx, role):
            return False

        user = ctx.author

        # If a user has this role, we will remove it
        if role in user.roles:
            if role.color.value == NATIVE_COLOR and not await self.__will_become_nativeless(ctx):
                return False

            await user.remove_roles(role, reason='self-removed')
            title = text_lines['roles']['assign']['removed'].format(role.name)

        # If a user doesn't have = we add
        else:
            # If a used doesn't have a native role we tell him to do that
            if not await self.__has_native_role(ctx):
                return False

            await user.add_roles(role, reason='self-added')
            title = text_lines['roles']['assign']['added'].format(role.name)

        embed = discord.Embed(title=title, colour=discord.Colour(MAIN_COLOR))

        await ctx.send(embed=embed)

    # Command for searching users who have multiple tags
    # Syntax is: ;who role1[, role2 ...]
    @commands.command(aliases=['who', 'inrole', 'inroles'])
    @commands.guild_only()
    async def search(self, ctx, *args):
        searching_roles = self.make_role_list(args)

        if await self.__basic_checks(ctx, searching_roles):
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
                                       description=text_lines['roles']['search']['no_users_title'],
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

            embed.add_field(name=header, value='\n'.join([member.display_name for member in found_users]), inline=True)
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
                row_users_list = [
                    self.shorten(member.display_name, settings['roles']['search']['max_length'])
                    for member in chunk[1]  # 1 cuz 0 is index
                ]
                embed.add_field(name=header, value='\n'.join(row_users_list), inline=True)

        await ctx.send(embed=embed)

    # Command for counting up users in following roles
    # Syntax is: ;count role1[, role2 ...]
    @commands.command()
    @commands.guild_only()
    async def count(self, ctx, *args):
        searching_roles = self.make_role_list(args)
        if await self.__basic_checks(ctx, searching_roles):
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
        if await self.__basic_checks(ctx, pinging_roles):
            server = ctx.guild
        else:
            return

        message = []
        gotta_change_later = []

        # You shouldn't be able to ping everyone and here
        for blacklist_item in settings['roles']['ping']['blacklist']:
            item = blacklist_item.lower()
            if item in pinging_roles:
                embed = error_embed(text_lines['roles']['ping']['cant_ping'].format(blacklist_item))
                await ctx.send(embed=embed)
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
            embed = error_embed(text_lines['roles']['less_than']['not_number'])
            await ctx.send(embed=embed)
            return

        # Too biggu nambaru?
        if x > settings['roles']['less_than']['limit']:
            embed = error_embed(text_lines['roles']['less_than']['too_big'])
            await ctx.send(embed=embed)
            return

        # Too sumarru nambaru?
        if x <= 0:
            embed = error_embed(text_lines['roles']['less_than']['too_small'])
            await ctx.send(embed=embed)
            return

        output = {role.name: len(role.members) for role in roles if len(role.members) < x}
        results = sorted(output.items(), reverse=True, key=operator.itemgetter(1))
        line = ', '.join([f"[{v}] {k}" for k, v in results])

        embed = discord.Embed(colour=discord.Colour(MAIN_COLOR),
                              title=text_lines['roles']['less_than']['title'].format(x),
                              description=line)

        await ctx.send(embed=embed)

    # Some helpful private functions

    # Basics check for commands if your arguments are roles
    async def __basic_checks(self, ctx, role_list) -> bool:
        if not self.__check_role_quantity(ctx, role_list) or not self.__check_if_role_exists(ctx, role_list):
            return False

        return True

    # No or too many roles given equals "Bye"
    async def __check_role_quantity(self, ctx, role_list) -> bool:
        if len(role_list) < 1 or len(role_list) > settings['roles']['search']['limit']:
            embed = error_embed(text_lines['roles']['search']['limit'].format(
                str(settings['roles']['search']['limit'])))
            await ctx.send(embed=embed)
            return False

    # Do these roles even exist?
    async def __check_if_role_exists(self, ctx, role_list) -> bool:
        server_roles = [role.name.lower() for role in ctx.guild.roles]

        # If we received a string in role_list then we gotta convert it to an array
        if isinstance(role_list, str):
            role_list = [role_list]  # (this is the worst code I ever wrote, gimme my java back)

        for role in role_list:
            if role.lower() not in server_roles:
                # If at least one doesn't = rip
                embed = error_embed(text_lines['roles']['search']['no_role'].format(role.title()))
                await ctx.send(embed=embed)
                return False
        return True

    # Checks if users can self-assign this role
    async def __check_allowability_of_role(self, ctx, role) -> bool:
        if not role.color.value in settings['roles']['assign']['allowed_colors']:
            embed = error_embed(text_lines['roles']['assign']['not_allowed'].format(role.name.title()))
            await ctx.send(embed=embed)
            return False

        return True

    # Returns true if user has AT LEAST ONE native role
    async def __has_native_role(self, ctx):
        user_roles = ctx.author.roles

        found = False

        for role in user_roles:
            if role.color.value == NATIVE_COLOR:
                found = True
                break

        if not found:
            embed = error_embed(text_lines['roles']['assign']['native_first'])
            await ctx.send(embed=embed)
            return False

        return found

    # Returns true will have 0 native roles after removing one
    async def __will_become_nativeless(self, ctx):
        user_roles = ctx.author.roles
        amount = 0

        for role in user_roles:
            if role.color.value == NATIVE_COLOR:
                amount = amount + 1

        if amount <= 1:
            embed = error_embed(text_lines['roles']['assign']['cant_remove_native'])
            await ctx.send(embed=embed)
            return False

        return True

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
