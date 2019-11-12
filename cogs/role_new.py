from typing import Union

import discord
from discord.ext import commands

from settings.config import settings
from settings.constants import ASSIGNABLE_ROLE_COLORS, NATIVE_COLOR, YES_EMOJI, INFO_COLOR, MAIN_COLOR, NO_EMOJI, \
    ADMIN_ROLES
from settings.lines import text_lines
from utils.utils import send_error_embed


class LinglotRole(commands.RoleConverter):
    async def convert(self, ctx, argument):
        try:
            return await super().convert(ctx, argument.title())
        except commands.BadArgument:
            return await super().convert(ctx, argument.capitalize())


class LinglotLanguageRole(LinglotRole):
    async def convert(self, ctx: commands.Context, argument):
        try:
            return await super().convert(ctx, ctx.invoked_with + ' ' + argument)
        except commands.BadArgument as BA:
            if ctx.invoked_with in ['native', 'fluent']:
                return await super().convert(ctx, argument)
            raise BA


class LinglotRoleList(LinglotRole):
    async def convert(self, ctx: commands.Context, argument):
        roles = argument.split(',')
        roles_new = []
        for role in roles:
            roles_new.append(await super().convert(ctx, role.strip()))
        return set(sorted(roles_new))  # Convert to a set here to ensure no duplicates


class RoleCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='role',
                      aliases=['native', 'fluent', 'learning'])
    @commands.guild_only()
    async def role_command(self, ctx: commands.Context, *, role: Union[LinglotRole, LinglotLanguageRole]):
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
            await ctx.author.add_roles(role, reason='self-added')
            embed = discord.Embed(title=text_lines['roles']['assign']['added'].format(role.name),
                                  colour=discord.Colour(MAIN_COLOR))
            await ctx.send(embed=embed)

    @commands.command(name='not')
    @commands.guild_only()
    async def role_remove_command(self, ctx: commands.Context, *, role: LinglotRole):
        if not self.is_assignable_role(role):
            # Role isn't self-assignable
            return await send_error_embed(ctx, text_lines['roles']['assign']['not_allowed'])

        if role not in ctx.author.roles:
            return await send_error_embed(ctx, text_lines['roles']['assign']['dont_have'])

        if self.native_role_count(ctx.author) == 1 and role.color.value == NATIVE_COLOR:
            return await send_error_embed(ctx, text_lines['roles']['assign']['cant_remove_native'])

        await ctx.author.remove_roles(role, reason='self-removed')
        embed = discord.Embed(title=text_lines['roles']['assign']['removed'].format(role.name),
                              color=discord.Color(MAIN_COLOR))

        await ctx.send(embed=embed)

    @role_command.error
    @role_remove_command.error
    async def role_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
            await send_error_embed(ctx, error.args[0])

        elif isinstance(error, commands.MissingRequiredArgument):
            await send_error_embed(ctx, text_lines['roles']['assign']['empty'])

        elif isinstance(error, commands.BadUnionArgument):
            role: str = ctx.message.content.replace(ctx.prefix + ctx.invoked_with + ' ', '')
            if ctx.invoked_with in ['fluent', 'native']:
                role = ctx.invoked_with + ' ' + role
            await send_error_embed(ctx, text_lines['roles']['search']['no_role'].format(role.title()))

    @commands.command(name='count')
    @commands.guild_only()
    async def count_command(self, ctx: commands.Context, *, roles: LinglotRoleList):
        if len(roles) > settings['roles']['search']['limit']:
            return await send_error_embed(ctx, text_lines['roles']['search']['limit']
                                          .format(settings['roles']['search']['limit']))

        total = sum(roles.issubset(user.roles) for user in ctx.guild.members)

        embed_body = ''

        for role in roles:
            users_in_role = sum(role in user.roles for user in ctx.guild.members)
            embed_body += text_lines['roles']['count']['total'].format(role.name, users_in_role)

        role_names = ', '.join(role.name for role in roles)
        if total <= 0:
            embed_title = text_lines['roles']['count']['no_users'].format(role_names)
        elif total == 1:
            embed_title = text_lines['roles']['count']['one_user'].format(role_names)
        else:
            embed_title = text_lines['roles']['count']['x_users'].format(total, role_names)

        embed = discord.Embed(title=embed_title,
                              color=discord.Color(MAIN_COLOR))
        if len(roles) > 1:
            embed.description = embed_body

        await ctx.send(embed=embed)

    @commands.command(name='search')
    @commands.guild_only()
    async def search_command(self, ctx: commands.Context, *, roles: LinglotRoleList):
        pass

    @count_command.error
    @search_command.error
    async def role_search_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
            await send_error_embed(ctx, 'Sorry, one or more of those roles does not exist!')

    @commands.command(name='ping')
    @commands.has_any_role(*ADMIN_ROLES)
    @commands.cooldown(rate=1, per=settings['roles']['ping']['cooldown'], type=commands.BucketType.user)
    @commands.guild_only()
    async def ping_command(self, ctx: commands.Context, *, roles: LinglotRoleList):
        pass

    @commands.command(name='top10', aliases=['top'])
    @commands.guild_only()
    async def top_roles_command(self, ctx: commands.Context):
        pass

    @commands.command(name='lessthan', aliases=['less'])
    @commands.has_any_role(*ADMIN_ROLES)
    @commands.guild_only()
    async def lessthan_command(self, ctx: commands.Context, target_size: int):
        if 0 <= target_size < settings['roles']['less_than']['limit']:
            await send_error_embed(ctx, 'Number out of range')

    @lessthan_command.error
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
    def is_assignable_role(role: discord.Role):
        """
        :param role: A Discord role
        :return: True if the role should be self-assignable, False otherwise
        """
        return role.color.value in ASSIGNABLE_ROLE_COLORS

    @staticmethod
    def native_role_count(user: discord.Member):
        """
        :param user: A Discord user
        :return: The number of native language roles the user has
        """
        return len([role for role in user.roles if role.color.value == NATIVE_COLOR])


def setup(bot: commands.Bot):
    bot.add_cog(RoleCommands(bot))
