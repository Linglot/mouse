"""
{} is a placeholder, be careful with it.
I.e. in 'My name is {}' it gets changed automatically to user's name.
After each line with a placeholder there's a comment with its 'future' content.
"""
from settings.constants import GITHUB_LINK, INV_LINK

text_lines = {
    ##############  IMPORTANT  ###############
    # Hierarchy: Cog (Class) -> Method -> Line
    'voice': {
        'change': {
            'must_be_in_vc': 'You must be in a voice channel',
            'cant_edit': 'Can\'t edit your channel\'s name. ',
            'empty': 'Please enter a language',
            'shorter': 'You could use name up to 20 symbols only',
            'done': 'Language set to {}',  # Language name
        },
        'reset': 'Channel name was reset to {}',  # Language name

        'format': '{} {} {}'  # VC name, Divider, Language
    },

    'roles': {
        'search': {
            'limit': 'You have to choose for at least 1 role and a maximum of {}',  # Number of maximum roles
            'no_role': 'There\'s no **{}** role on the server',  # Role name
            'no_users_title': 'No users were found',
            'try_again': 'Maybe you should try another combination?',
            'one_user': '1 user for: {}',  # Role list
            'x_users': '{} users for: {}',  # Number of users, Role list
            'one_user_header': 'The one and only',
            'many_users_header': '{}-{}',  # Start number, End number
            'and_more': 'And {} more…'  # A number of users
        },
        'count': {
            'x_users': '{} users match the combination: {}',  # Total umber of users, Role list
            'one_user': '1 user match the combination: {}',  # Role list
            'no_users': 'No users match the combination: {}',  # Role list
            'total': 'Total in {}: **{}**\n'  # Role name, Number of users
        },

        'ping': {
            'cant_ping': 'You can\'t ping `{}`',  # Role name

            # Errors
            'slow_down_m': 'You can\'t ping again for {} minutes',  # Minutes
            'slow_down_s': 'You can\'t ping again for {} seconds',  # Seconds
            'no_access': 'You don\'t have the permissions to this command'
        },
        'less_than': {
            'not_number': 'r u dumb? gimme an integer',
            'too_big': 'u gave m-me such a b-big n-number, s-sempai uwu',
            'too_small': 'u gave m-me such a small n-number, s-sempai uwu (more than 0 pls)',
            'title': 'Roles with fewer than {} members'  # Number of members
        }
    },

    'server_info': {
        'titles': {
            'id': 'Id',
            'owner': 'Owner',
            'region': 'Region',
            'roles': 'Roles: {}',  # Amount of roles
            'features': 'Features',
            'default_channel': 'Default channel',
            'channels': 'Channels: {}',  # Amount of channels
            'created_at': 'Created at',
            'members': 'Members: {}',  # Amount of members
            'emojis': 'Emojis: {}'  # Amount of emojis
        },
        'members_line': '{} tagged, {} normies',  # In total, Without roles
        'roles': '{} language, {} other',  # Amount of language roles, Amount of other roles
        'channel_line': '{} text, {} voice'  # Text channels, Voice channels
    },

    # Text lines for ;info command
    'about': {
        'about_desc': 'Heyo! This bot was developed specially for the Linglot server. '
                      'If you have any suggestions or bug reports, please contact the server staff.',
        'about_gh_link': ':notepad_spiral: Github',
        'about_gh_desc': 'If you want to help us with our bot, or just look at our ~~crappy~~ code,'
                         'you can do it [here]({})'
            .format(GITHUB_LINK),
        'about_inv_link': ':u6708: Linguistic lot',
        'about_inv_desc': 'Here\'s an [invite link]({}) for you, if you want to join our server'
            .format(INV_LINK)
    },

    # Text lines for ;version command
    'version': {
        'version_currently': 'Current version is {}!',  # Version number
        'version_footer': 'Sincerely yours, {}'  # Bot's name
    },

    # Text lines for ;version command
    'github': {
        'github': 'Github'
    },

    # Some lines for 'oopsie' stuff
    'technical': {
        'forbidden': 'I don\'t have access to write to #{} on {}',  # Channel name, Server name
        'cant_do_in_pm': 'I can\'t perform this command in DMs',
        'none': 'None',
        'unknown_error': 'An unknown error has happened, pls report this line to the bot devs. arigato'
                         '\n\n**Copy and paste this**\n`{}`'  # Error line
    },

    'logging': {
        'lang_removed': 'Language tag removed from {}',  # Channel name\
        'command_sent': '{}#{} sent \'{}\' in #{}'  # Name#0000, Command, Channel
    },
}
