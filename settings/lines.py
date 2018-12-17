"""
{} is a placeholder, be careful with it.
I.e. in "My name is {}" it gets changed automatically to user's name.
After each line with a placeholder there's a comment with its "future" content.
"""
from settings import config

text_lines = {
    # Text lines for ;lang and ;resetlang functions
    'voice_channel_language': {
        'lang_if_nothing': [
            "Language set to absolutely nothing",
            "What about you try giving me a language?",
            "Which language do you want hey?",
            "Please enter a language"
        ],
        'lang_make_shorter': "You could use name up to 20 symbols only",
        'lang_were_set': "Language set to {}",  # Language name
        'lang_were_reset': "Channel name was reset to {}",  # Language name
        'lang_cant_edit': "Can't edit that channel's name. Try other ones, such as Lobby, Park, Practice or Lecture Hall",
        'lang_must_be_in_vc': "You must be in a voice channel"

    },

    # Text lines for ;who command
    'combined_search': {
        'min_max_roles_amount': "You have to search for at least 1 role and a maximum of {}",  # Number of maximum roles
        'no_such_role': "There's no **{}** role on the server",  # Role name
        'no_users_found': "No users were found",
        'try_another_one': "Maybe you should try another combination?",
        'x_users_for': "{} users for: {}",  # Number of users, Role list
        'one_user_for': "1 user for: {}",  # Role list
        'one_user_column_header': "The one and only",
        'many_user_column_header': "{}-{}",  # Start number, End number
        'and_many_more': "And {} more…"  # A number of users

        ### These are not in use for now ###
        ####################################
        # 'row_1_column': "Total # of users",
        # 'row_2_column'
        # 'row_3_column': "☆",
        # 'row_1_column_only': "Results are: ",  # when <6 results, this text is shown instead of 'row_1_column"
    },

    'role_count': {
        "x_number_of_users": "{} users match following combination: {}",  # Total umber of users, Role list
        "total_in_role": "Total in **{}**: **{}**\n"  # Role name, Number of users
    },

    # Text lines for ;info command
    'about': {
        'about_desc': "Heyo! This bot was developed specially for the Linglot server. "
                      "If you have any suggestions or bug reports, please contact the server staff.",
        'about_gh_link': ":notepad_spiral: Github",
        'about_gh_desc': "If you want to help us with our bot, or just look at our ~~crappy~~ code,"
                         "you can do it [here]({})"
            .format(config.GITHUB_LINK),
        'about_inv_link': ":u6708: Linguistic lot",
        'about_inv_desc': "Here's an [invite link]({}) for you, if you want to join our server"
            .format(config.INV_LINK)
    },

    # Text lines for ;version command
    'version': {
        'version_currently': "Current version is {}!",  # Version number
        'version_footer': "Sincerely yours, {}"  # Bot's name
    }
}
