from settings.config import MAIN_COLOR, settings
from settings.lines import text_lines
from utils.tools import *


# TODO: This whole code needs reviewing and refactoring in the future.

# Command for searching users who have multiple tags
async def role_search(bot, server, channel, searching_roles):
    found_users = []

    # No or too many roles given equals "Bye"
    if len(searching_roles) < 1 or len(searching_roles) > settings['combined_search']['role_limit']:
        embed = error_embed(text_lines['combined_search']['min_max_roles_amount'].format(
            str(settings['combined_search']['role_limit'])))
        await bot.send_message(channel, embed=embed)
        return

    # Do these roles even exist?
    server_roles = [role.name.lower() for role in server.roles]
    for role in searching_roles:
        # If at least one doesn't = rip
        if role not in server_roles:
            embed = error_embed(text_lines['combined_search']['no_such_role'].format(role.title()))
            await bot.send_message(channel, embed=embed)
            return

    # Looking for peeps
    for member in server.members:
        user_roles = [str(role).lower() for role in member.roles]
        if set(searching_roles).issubset(user_roles):
            found_users.append(member)

    # If the result is 0 peeps, we have to show that
    number_of_results = len(found_users)
    if number_of_results == 0:
        no_results = discord.Embed(title=text_lines['combined_search']['no_users_found'],
                                   description=text_lines['combined_search']['try_another_one'],
                                   colour=discord.Colour(MAIN_COLOR))

        await bot.send_message(channel, embed=no_results)
        return

    # Making the title string ready
    if number_of_results == 1:
        title = text_lines['combined_search']['one_user_for'].format(
            ", ".join([role.title() for role in searching_roles]))
    else:
        title = text_lines['combined_search']['x_users_for'].format(
            number_of_results, ", ".join([role.title() for role in searching_roles]))

    embed = discord.Embed(title=title, colour=discord.Colour(MAIN_COLOR))

    if number_of_results < 6:
        if number_of_results == 1:
            header = text_lines['combined_search']['one_user_column_header']
        else:
            header = text_lines['combined_search']['many_user_column_header'].format(1, number_of_results)

        embed.add_field(name=header,
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
        column_end_number = 0
        for i, chunk in enumerate(create_chunks(found_users, 3)):
            # Bunch of useless variables, but it's better to use them
            # than count this stuff on the fly.
            old_cz = column_end_number + 1
            column_end_number += len(chunk)
            header = text_lines['combined_search']['many_user_column_header'].format(old_cz, column_end_number)

            row_users_list = [
                add_dots(member.display_name, settings['combined_search']['max_user_name_length'])
                for member in chunk
            ]
            embed.add_field(name=header, value='\n'.join(row_users_list), inline=True)

    await bot.send_message(channel, embed=embed)


# Command for searching users who have multiple tags
# TODO: Remove code duplication in this in ;who
async def role_count(bot, server, channel, searching_roles):
    # No or too many roles given equals "Bye"
    if len(searching_roles) < 1 or len(searching_roles) > settings['combined_search']['role_limit']:
        embed = error_embed(text_lines['combined_search']['min_max_roles_amount'].format(
            str(settings['combined_search']['role_limit'])))
        await bot.send_message(channel, embed=embed)
        return

    # Do these roles even exist?
    server_roles = [role.name.lower() for role in server.roles]
    for role in searching_roles:
        # If at least one doesn't = rip
        if role not in server_roles:
            embed = error_embed(text_lines['combined_search']['no_such_role'].format(role.title()))
            await bot.send_message(channel, embed=embed)
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
        description_line += text_lines['role_count']['total_in_role'].format(role.title(), cur_res)

    roles = ", ".join([role.title() for role in searching_roles])

    if users_in_combination <= 0:
        title = text_lines['role_count']['none_users_in_combination'].format(roles)
    elif users_in_combination == 1:
        title = text_lines['role_count']['one_user_in_combination'].format(roles)
    else:
        title = text_lines['role_count']['x_number_of_users'].format(users_in_combination, roles)

    if len(searching_roles) > 1:
        embed = discord.Embed(title=title,
                              description=description_line,
                              colour=discord.Colour(MAIN_COLOR))
    else:
        embed = discord.Embed(title=title,
                              colour=discord.Colour(MAIN_COLOR))

    await bot.send_message(channel, embed=embed)
