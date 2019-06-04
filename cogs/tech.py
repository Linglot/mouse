from discord.ext import commands


# There's only a skeleton for future commands that would work with wiki.
# Basically the idea was loading all the info from wiki into the bot
# Then using it.
# If there was an update on wiki, admins could use these commands to make bot update all the information.

# In theory this is not a bad implementation cuz we can story some kind of cache of it, also prevents wiki vandalization
# Because the information won't be updated when the wiki was griffered
class TechCommands:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    def update_faq_translations(self):
        pass

    @commands.command()
    def update_lang_aliases(self):
        pass


def setup(bot):
    bot.add_cog(TechCommands(bot))
