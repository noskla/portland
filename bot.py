import discord, logging, sys
from config import Config


class Portland(discord.Client):

    def __init__(self, *args, **kwargs):
        super(Portland, self).__init__(*args, **kwargs)
        self.discoLogger, self.discoLogFile = None, None
        self.init_logger()

        try:
            self.run(Config.discord_token)
        except discord.errors.LoginFailure:
            sys.exit('Token is incorrect. Please use one from a valid bot account on https://discord.com/developers/')

    def init_logger(self):
        self.discoLogger = logging.getLogger('discord')
        self.discoLogger.setLevel(logging.INFO)
        self.discoLogFile = logging.FileHandler(filename='portland.log', encoding='utf-8', mode='w')
        self.discoLogger.addHandler(self.discoLogFile)

    async def on_ready(self):
        print('Portland is connected to Discord and logged in as {}'.format(self.user.name))


