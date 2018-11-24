import _config
"""
{} - Placeholder, be careful with it.
I.e. in "My name is {}" it gets changed automatically to user's name.
After each line with a placeholder there's a comment with its "future" content.
"""

# ;lang && ;l command replies
lang_if_nothing = [
	"Language set to absolutely nothing",
	"What about you try giving me a language?",
	"Which language do you want hey?",
	"Please enter a language"
]
lang_make_shorter = "You could use name up to 20 symbols only"
lang_were_set = "Language set to {}" #Language name
lang_were_reset = "Channel name was reset to {}" #Language name
lang_cant_edit = "Can't edit that channel's name. Try other ones, such as Lobby, Park, Practice or Lecture Hall"
lang_must_be_in_vc = "You must be in a voice channel"

about_desc = "Heyo! This bot was developed specially for Linglot server. " \
			 "If you have any suggestions or you've found a bug, please contact server staff."
about_gh_link   = ":notepad_spiral: Github"
about_gh_desc   = "If you want to help us with our bot or just look at our ~~crappy~~ code, you can do it [here]({})".format(_config.GITHUB_LINK)
about_inv_link  = ":u6708: Linguistic lot"
about_inv_desc  = "Here's an [invite link]({}) for you, if you want to join our server".format(_config.INV_LINK) # TODO: Prolly needs changing, but not now

version_currently = "Current version is {}!" # Version number
version_footer = "Sincerely yours, {}" # Bot's name