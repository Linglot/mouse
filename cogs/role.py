import operator
from typing import Union

import discord
from discord.ext import commands

from settings.config import settings
from settings.constants import ASSIGNABLE_ROLE_COLORS, NATIVE_COLOR, YES_EMOJI, INFO_COLOR, MAIN_COLOR, NO_EMOJI, \
    ADMIN_ROLES
from settings.lines import text_lines
from utils.utils import send_error_embed, chunks


# Basically, this lets us specify that a command requires a *valid role* as an argument.
# We inherit RoleConverter, which makes sure that the passed argument is a *valid role*.
# Language names on Linglot are usually "<level> <language>" (e.g. "Learning Italian", or "Learning Japanese"),
# where the entire string is title-case. So, first we try the argument passed but forced to title-case.
# If that's not a valid role, e.g. in the case of "Correct me!" it would try "Correct Me!" which is wrong, we try
# just to capitalise the first letter of the argument and check if *that* is a valid role.
# See https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html#advanced-converters
class LinglotRole(commands.RoleConverter):
    async def convert(self, ctx, argument):
        try:
            return await super().convert(ctx, argument.title())
        except commands.BadArgument:
            return await super().convert(ctx, argument.capitalize())


# for ;native, ;fluent, and ;learning
class LinglotLanguageRole(LinglotRole):
    async def convert(self, ctx: commands.Context, argument):
        try:
            return await super().convert(ctx, ctx.invoked_with + ' ' + argument)
        except commands.BadArgument as BA:
            # some languages are merged and do not have separate native/fluent roles
            if ctx.invoked_with in ['native', 'fluent']:
                return await super().convert(ctx, argument)
            raise BA


class LinglotRoleList(LinglotRole):
    async def convert(self, ctx: commands.Context, argument):
        roles = argument.split(',')
        roles_new = []
        for role in roles:
            roles_new.append(await super().convert(ctx, role.strip()))
        # Convert to a set here to ensure there are no duplicates
        return set(sorted(roles_new))


class RoleCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='role', aliases=['native', 'fluent', 'learning'])
    @commands.guild_only()
    async def role_command(self, ctx: commands.Context, *, role: Union[LinglotRole, LinglotLanguageRole]):
        # noinspection PyTypeChecker
        if not self.is_assignable_role(role):
            # Role isn't self-assignable
            return await send_error_embed(ctx, text_lines['roles']['assign']['not_allowed'])

        if role in ctx.author.roles:
            if self.native_role_count(ctx.author) == 1 and role.color.value == NATIVE_COLOR:
                # User is trying to remove their only native role
                return await send_error_embed(ctx, text_lines['roles']['assign']['cant_remove_native'])
            else:
                return await self.yes_no_dialogue(ctx, role)
        else:
            if self.native_role_count(ctx.author) == 0 and role.color.value != NATIVE_COLOR:
                # User does not have a native role, they should add one first!
                return await send_error_embed(ctx, text_lines['roles']['assign']['native_first'])
            # add the user to the role, then let them know it was successful
            await ctx.author.add_roles(role, reason='self-added')
            embed = discord.Embed(title=text_lines['roles']['assign']['added'].format(role.name),
                                  colour=discord.Colour(MAIN_COLOR))
            await ctx.send(embed=embed)

    @commands.command(name='not')
    @commands.guild_only()
    async def role_remove_command(self, ctx: commands.Context, *, role: LinglotRole):
        # noinspection PyTypeChecker
        if not self.is_assignable_role(role):
            # Role isn't self-assignable
            return await send_error_embed(ctx, text_lines['roles']['assign']['not_allowed'])

        if role not in ctx.author.roles:
            # User does not have the role
            return await send_error_embed(ctx, text_lines['roles']['assign']['dont_have'])

        if self.native_role_count(ctx.author) == 1 and role.color.value == NATIVE_COLOR:
            # User is trying to remove their only native role
            return await send_error_embed(ctx, text_lines['roles']['assign']['cant_remove_native'])

        await ctx.author.remove_roles(role, reason='self-removed')
        embed = discord.Embed(title=text_lines['roles']['assign']['removed'].format(role.name),
                              color=discord.Color(MAIN_COLOR))

        await ctx.send(embed=embed)

    @role_command.error
    @role_remove_command.error
    async def role_error(self, ctx: commands.Context, error):
        # User provided a non-existent role to ;not
        if isinstance(error, commands.BadArgument):
            await send_error_embed(ctx, error.args[0])

        # User didn't provide any roles
        elif isinstance(error, commands.MissingRequiredArgument):
            await send_error_embed(ctx, text_lines['roles']['assign']['empty'])

        # User provided a non-existent role to ;role or ;fluent or ;native
        elif isinstance(error, commands.BadUnionArgument):
            role: str = ctx.message.content.replace(ctx.prefix + ctx.invoked_with + ' ', '')
            if ctx.invoked_with in ['fluent', 'native']:
                role = ctx.invoked_with + ' ' + role
            await send_error_embed(ctx, text_lines['roles']['search']['no_role'].format(role.title()))

    @commands.command(name='count')
    @commands.guild_only()
    async def count_command(self, ctx: commands.Context, *, roles: LinglotRoleList):
        # noinspection PyTypeChecker
        if len(roles) > settings['roles']['search']['limit']:
            return await send_error_embed(ctx, text_lines['roles']['search']['limit']
                                          .format(settings['roles']['search']['limit']))

        # Find total users who have *all* of the provided roles
        total = sum(roles.issubset(user.roles) for user in ctx.guild.members)

        embed_body = ''

        # noinspection PyTypeChecker
        # Generate a list of how many users have *each* role
        for role in roles:
            users_in_role = sum(role in user.roles for user in ctx.guild.members)
            embed_body += text_lines['roles']['count']['total'].format(role.name, users_in_role)

        # noinspection PyTypeChecker
        role_names = ', '.join(role.name for role in roles)
        if total <= 0:
            embed_title = text_lines['roles']['count']['no_users'].format(role_names)
        elif total == 1:
            embed_title = text_lines['roles']['count']['one_user'].format(role_names)
        else:
            embed_title = text_lines['roles']['count']['x_users'].format(total, role_names)

        embed = discord.Embed(title=embed_title,
                              color=discord.Color(MAIN_COLOR))
        # noinspection PyTypeChecker
        # If we're looking for a combination of roles, put the totals for each role in the embed body
        if len(roles) > 1:
            embed.description = embed_body

        await ctx.send(embed=embed)

    @commands.command(name='search', aliases=['who', 'inrole', 'inroles'])
    @commands.guild_only()
    async def search_command(self, ctx: commands.Context, *, roles: LinglotRoleList):
        found = []
        for member in ctx.guild.members:
            if roles.issubset(member.roles):
                found.append(member)

        title_line = ", ".join(role.name for role in roles)

        if not len(found):
            no_results = discord.Embed(title=text_lines['roles']['search']['no_users_title'],
                                       description=text_lines['roles']['search']['try_again'],
                                       colour=discord.Colour(MAIN_COLOR))
            return await ctx.send(embed=no_results)
        elif len(found) == 1:
            title = text_lines['roles']['search']['one_user'].format(title_line)
        else:
            title = text_lines['roles']['search']['x_users'].format(len(found), title_line)

        embed = discord.Embed(title=title, color=discord.Colour(MAIN_COLOR))

        if len(found) < 6:
            if len(found) == 1:
                header = text_lines['roles']['search']['one_user_header']
            else:
                header = text_lines['roles']['search']['many_users_header'].format(1, len(found))

            embed.add_field(name=header, value="\n".join(member.display_name for member in found), inline=True)
        else:
            if len(found) > 30:
                embed.set_footer(text=text_lines['roles']['search']['and_more'].format(len(found) - 30))
            chunked_list = list(chunks(found[:30], 10))
            ranges = [[found.index(chunk[0]) + 1, found.index(chunk[-1]) + 1] for chunk in chunked_list]
            for i in range(0, len(chunked_list)):
                header = text_lines['roles']['search']['many_users_header'].format(*ranges[i])
                members = "\n".join(
                    member.display_name[:settings['roles']['search']['max_length']] for member in chunked_list[i]
                )
                embed.add_field(name=header, value=members, inline=True)

        return await ctx.send(embed=embed)

    @count_command.error
    @search_command.error
    async def role_search_error(self, ctx: commands.Context, error):
        # user provided one or more non-existent roles
        if isinstance(error, commands.BadArgument):
            await send_error_embed(ctx, 'Sorry, one or more of those roles does not exist!')

        # user provided no roles
        elif isinstance(error, commands.MissingRequiredArgument):
            await send_error_embed(ctx, 'You must provide one or more roles for this command!')

    # we specify cooldown_after_parsing=True so that ping commands that fail due to non-existent roles, or no arguments,
    # don't trigger a cooldown,
    @commands.command(name='ping', cooldown_after_parsing=True)
    @commands.has_any_role('Event Host', *ADMIN_ROLES)
    @commands.cooldown(rate=1, per=settings['roles']['ping']['cooldown'], type=commands.BucketType.user)
    @commands.guild_only()
    async def ping_command(self, ctx: commands.Context, *, roles: LinglotRoleList):
        # Make sure the user is not trying to ping any blacklisted roles
        # noinspection PyTypeChecker
        if any([role.name in settings['roles']['ping']['blacklist'] for role in roles]):
            return await send_error_embed(ctx, 'Sorry, one or more of those roles is not ping-able!')

        # noinspection PyTypeChecker
        await ctx.send(f"PING! {ctx.author.mention} is pinging {', '.join(role.mention for role in roles)}")

    @ping_command.error
    async def ping_error(self, ctx: commands.Context, error):
        # User did not provide a valid list of roles
        if isinstance(error, commands.BadArgument):
            await send_error_embed(ctx, 'Sorry, one or more of those roles does not exist!')

        # user provided no roles
        elif isinstance(error, commands.MissingRequiredArgument):
            await send_error_embed(ctx, 'Sorry, you need to provide at least one role to ping')

        # User is hitting cooldown for this command
        elif isinstance(error, commands.CommandOnCooldown):
            # If the command is on cooldown, but the person trying to use it is an admin...
            if self.user_is_admin(ctx.message.author):
                # ... then bypass the cooldown and let them use it!
                await ctx.reinvoke()
            else:
                await send_error_embed(ctx, 'Sorry, this command is on cooldown!')

    @commands.command(name='top10', aliases=['top'])
    @commands.guild_only()
    async def top_roles_command(self, ctx: commands.Context):
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

    @commands.command(name='lessthan', aliases=['less'])
    @commands.has_any_role(*ADMIN_ROLES)
    @commands.guild_only()
    async def less_than_command(self, ctx: commands.Context, target_size: int):

        # make sure the target role size is within the right limits
        if target_size <= 0 or target_size > settings['roles']['less_than']['limit']:
            return await send_error_embed(ctx, 'Number out of range')

        # generate the list, greatest to least, of the roles with less than `target_size` members
        output = {role.name: len(role.members) for role in ctx.guild.roles if len(role.members) < target_size}
        results = sorted(output.items(), reverse=True, key=operator.itemgetter(1))
        line = ', '.join([f"[{v}] {k}" for k, v in results])

        # The list of roles has the potential to be over 2000 characters, which is the max amount of characters
        # discord allows you to send in a message. Truncate it if it's too long
        # TODO probably find a more elegant way to do this
        if len(line) > 2000:
            line = line[:1996] + '...'

        embed = discord.Embed(colour=discord.Colour(MAIN_COLOR),
                              title=text_lines['roles']['less_than']['title'].format(target_size),
                              description=line)

        await ctx.send(embed=embed)

    @less_than_command.error
    async def lessthan_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await send_error_embed(ctx, 'You must pass a number to this command')

    async def yes_no_dialogue(self, ctx, role):
        # TODO: fix this trash fire
        embed = discord.Embed(title=text_lines['roles']['assign']['already_have_title'],
                              description=text_lines['roles']['assign']['already_have_msg'],
                              colour=discord.Colour(INFO_COLOR))
        msg = await ctx.send(embed=embed)
        await msg.add_reaction(YES_EMOJI)
        await msg.add_reaction(NO_EMOJI)

        try:
            reaction, user = await self.bot.wait_for('reaction_add',
                                                     timeout=settings['roles']['assign']['emoji_cd'],
                                                     check=lambda r, u: r.message.id == msg.id and u == ctx.author)
        except TimeoutError:
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

    @staticmethod
    def user_is_admin(member: discord.Member):
        """
        :param member: A discord guild member
        :return: True if the user is a server admin, False otherwise
        """
        return any(role.name.title() in ADMIN_ROLES for role in member.roles)

    @staticmethod
    def is_assignable_role(role: discord.Role):
        """
        :param role: A Discord guild role
        :return: True if the role should be self-assignable, False otherwise
        """
        return role.color.value in ASSIGNABLE_ROLE_COLORS

    @staticmethod
    def native_role_count(user: discord.Member):
        """
        :param user: A Discord guild member
        :return: The number of native language roles the user has
        """
        return len([role for role in user.roles if role.color.value == NATIVE_COLOR])

    @staticmethod
    def __make_top10_lines(roles):
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


def setup(bot: commands.Bot):
    bot.add_cog(RoleCommands(bot))
