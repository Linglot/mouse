import asyncio
from collections import OrderedDict

import more_itertools
from discord.ext import commands

from settings.config import settings
from settings.constants import MAIN_COLOR, NATIVE_COLOR, YES_EMOJI, NO_EMOJI
from settings.lines import text_lines
from utils.utils import *


# This class designed for any role-interaction commands for users
class RoleCommands:
    def __init__(self, bot):
        self.bot = bot

    # Command for role assigning.
    # It has multiple aliases which are adding either "native", "fluent", or "learning".
    # ;role alias is a normal one and can be used for any role basically.
    # ;role is used to add a role. If a person already has that role there will be a "yes-no" dialogue
    # ;native, fluent, ;learning could be used as a replacement of `;role native X` etc. Also shows the yes-no dialogue
    # ;not is only used to remove the role. The yes-no dialogue WILL NOT be shown
    @commands.command(aliases=['role', 'native', 'fluent', 'learning', 'not'])
    @commands.guild_only()
    async def role_assign(self, ctx, *args):
        role_name = ' '.join(args).title()
        called_with = ctx.invoked_with

        # Empty argument = bye
        if len(role_name.strip()) <= 0:
            await send_error_embed(ctx, (text_lines['roles']['assign']['empty']))
            return

        # We have to add some strings to make aliases searchable
        if called_with == 'native' or called_with == 'fluent' or called_with == 'learning':
            role_name = called_with.title() + ' ' + role_name

        splitted_name = role_name.split(' ')

        # If a person typed lets say ;fluent belorussian, but we only have Belorusian as a native-like (Blue) role
        # Basically a hack for smaller roles without native \ fluent division
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

        # Check for basic stuff like number of arguments and existing of each role
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

        # If the result is 0 peeps, we have to display that
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

        # (1 column output) If there's not so many users this will make output more good looking
        if number_of_results < 6:
            if number_of_results == 1:
                header = text_lines['roles']['search']['one_user_header']
            else:
                header = text_lines['roles']['search']['many_users_header'].format(1, number_of_results)

            member_list = '\n'.join([member.display_name for member in found_users])
            embed.add_field(name=header, value=member_list, inline=True)
        # 3 columns output (when there's a lot of users)
        else:
            # if there's more than 30 users, we don't need to display the others
            # Also this is NOT(!) a changeable option due to discord limits
            if number_of_results > 30:
                found_users = [user for i, user in enumerate(found_users) if i < 30]
                excluded = number_of_results - 30
                embed.set_footer(text=text_lines['roles']['search']['and_more'].format(excluded))

            # Dividing roles by the 3 chunks, removing long names and making columns
            column_end_number = 0

            # Basically a loop for 1, 2 and 3 chunk, adding each to output
            for chunk in enumerate(self.__create_chunks(found_users, 3)):
                # Bunch of useless variables, but it's better to use them than count this stuff on the fly.
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

        # Check for basic stuff like number of arguments and existing of each role
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

        # Deciding which title do we want to use
        if users_in_combination <= 0:
            title = text_lines['roles']['count']['no_users'].format(roles)
        elif users_in_combination == 1:
            title = text_lines['roles']['count']['one_user'].format(roles)
        else:
            title = text_lines['roles']['count']['x_users'].format(users_in_combination, roles)

        # If we were looking for more than 1 role, we have to output all of them
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

        # Check for basic stuff like number of arguments and existing of each role
        if await self.multirole_checks(ctx, pinging_roles):
            server = ctx.guild
        else:
            return

        message = []
        gotta_change_later = []

        # You shouldn't be able to ping everyone and here, and some other roles
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

    # Some tech functions

    # Basics check for commands if your want to check multiple roles
    # Check for basic stuff like number of arguments and existing of each role
    async def multirole_checks(self, ctx, role_list) -> bool:
        if not await self.check_search_limit(role_list):
            await send_error_embed(ctx, (text_lines['roles']['search']['limit'].format(
                str(settings['roles']['search']['limit']))))
            return False

        if not await self.is_role_exist(ctx, role_list, output=True):
            return False

        return True

    # Check for role amount limit/
    async def check_search_limit(self, role_list) -> bool:
        return 1 <= len(role_list) <= settings['roles']['search']['limit']

    # Do(es) certain role(s) even exist?
    # Output is false by default, put it yes if you want to make error message like
    # `Role X doesn't exist on the server`
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

    # Creates a yes-no embed dialogue for role selection commands
    async def role_yes_no_dialogue(self, ctx, role):
        embed = discord.Embed(title=text_lines['roles']['assign']['already_have_title'],
                              description=text_lines['roles']['assign']['already_have_msg'],
                              colour=discord.Colour(INFO_COLOR))
        msg = await ctx.send(embed=embed)

        # Adding yes no buttons
        await msg.add_reaction(YES_EMOJI)
        await msg.add_reaction(NO_EMOJI)

        def check(c_reaction, c_user):
            return c_reaction.message.id == msg.id and c_user == ctx.author

        # Waiting for a user to react
        try:
            reaction, user = await self.bot.wait_for('reaction_add',
                                                     timeout=settings['roles']['assign']['emoji_cd'],
                                                     check=check)
        # If they ignored our beautiful dialogue, we'll just removing the emojis
        except asyncio.TimeoutError:
            await msg.clear_reactions()
            embed = discord.Embed(title=text_lines['roles']['assign']['keep'].format(role.name),
                                  colour=discord.Colour(MAIN_COLOR))
            await msg.edit(embed=embed)
        # Otherwise if they were actually smart and pressed something we're doing the stuff
        else:
            if reaction.emoji == YES_EMOJI:
                await user.remove_roles(role, reason='self-removed')
                embed = discord.Embed(title=text_lines['roles']['assign']['removed'].format(role.name),
                                      colour=discord.Colour(MAIN_COLOR))
            else:
                embed = discord.Embed(title=text_lines['roles']['assign']['keep'].format(role.name),
                                      colour=discord.Colour(MAIN_COLOR))

            # Editing the previous message to show the results to user, removing emojis
            await msg.edit(embed=embed)
            await msg.clear_reactions()

    # Static methods

    # Divides list into N evenly-sized chunks
    @staticmethod
    def __create_chunks(list_to_divide, number_of_chunks):
        return [list(c) for c in more_itertools.divide(number_of_chunks, list_to_divide)]

    # Dividing roles to a list, removing unnecessary spaces and making it lowercase
    # "  native english,    fluent english " -> ["native english", "fluent english"]
    # (prolly should've make a more good-looking name)
    @staticmethod
    def make_role_list(role_string):
        result = [role.strip().lower() for role in " ".join(role_string).split(",") if role.strip() != ""]
        return list(OrderedDict.fromkeys(result))

    # Add a … symbol if the string (username, basically) is longer than "limit"
    @staticmethod
    def shorten(string, limit) -> str:
        # "…" " " - 3 dots + 2x unbreakable spaces (alt+0160)
        return (string[:limit] + '…  ') if len(string) > limit else string


def setup(bot):
    bot.add_cog(RoleCommands(bot))
