import operator
from collections import OrderedDict

import more_itertools
from discord.ext import commands

from settings.config import settings
from settings.constants import MAIN_COLOR
from settings.lines import text_lines
from utils.utils import *


class RoleCommands:

    def __init__(self, bot):
        self.bot = bot

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
                found_users = [user for i, user in enumerate(found_users) if i < 10 * 3]
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
    # Syntax is: ;ping
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

        role_dict = {}
        for role in server.roles:
            role_dict[role.name] = len(role.members)

        # Larger ones first
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

    # # Searches for roles with less than X members
    # # Syntax: ;lessthan 10
    # TODO
    # @commands.command(aliases=["lessthan", "less"], pass_context=True)
    # @commands.has_any_role(*MOD_ROLES)
    # async def less_than(self, ctx, *args):
    #     server = ctx.message.server
    #     channel = ctx.message.channel
    #     x = int("".join(args))
    #
    #     await info.less_than(self.bot, server, channel, x)

    async def __basic_checks(self, ctx, role_list) -> bool:
        # No or too many roles given equals "Bye"
        if len(role_list) < 1 or len(role_list) > settings['roles']['search']['limit']:
            embed = error_embed(text_lines['roles']['search']['limit'].format(
                str(settings['roles']['search']['limit'])))
            await ctx.send(embed=embed)
            return False

        # Do these roles even exist?
        server_roles = [role.name.lower() for role in ctx.guild.roles]
        for role in role_list:
            if role not in server_roles:
                # If at least one doesn't = rip
                embed = error_embed(text_lines['roles']['search']['no_role'].format(role.title()))
                await ctx.send(embed=embed)
                return False

        return True

    # Divides list into N evenly-sized chunks
    @staticmethod
    def __create_chunks(list_to_divide, number_of_chunks):
        return [list(c) for c in more_itertools.divide(number_of_chunks, list_to_divide)]

    # Static methods

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
