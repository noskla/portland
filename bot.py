import discord, logging, sys, asyncio, psutil
from config import Config
from commandhandler import CommandHandler


class Portland(discord.Client):

    def __init__(self, *args, **kwargs):
        super(Portland, self).__init__(*args, **kwargs)
        self.command_handler = CommandHandler()
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
        self.command_handler.start_voice_info_loop(self)
        if not Config.voice_auto_join or not self.command_handler.voice.voice_enabled:
            return
        channel = self.get_channel(Config.voice_auto_join_channel_id)
        while 1:
            member_count = len([a for a in channel.members if not a.id == self.user.id])
            if channel.guild.voice_client is None and member_count > 0 and Config.voice_auto_join:
                channel = self.get_channel(Config.voice_auto_join_channel_id)
                self.command_handler.voice.voice_channels[channel.guild.id] = await channel.connect(timeout=15,
                                                                                                    reconnect=True)
                if not self.command_handler.voice.voice_channels[channel.guild.id].is_playing():
                    self.command_handler.voice.voice_channels[channel.guild.id].play(
                        self.command_handler.voice.audio_source)

            elif channel.guild.voice_client is not None and not member_count and Config.voice_auto_join:
                self.command_handler.voice.voice_channels[channel.guild.id].stop()
                await self.command_handler.voice.voice_channels[channel.guild.id].disconnect()
                for proc in psutil.Process().children(recursive=True):
                    if 'ffmpeg' in proc.name():
                        proc.kill()
                self.command_handler.voice.voice_channels.pop(channel.guild.id)
                self.command_handler.voice.restart_source()
            await asyncio.sleep(5)

    async def on_message(self, msg):
        if not msg.content.startswith(Config.default_prefix) or msg.author.bot:
            return
        try:
            command, arguments = msg.content.split(' ', 1)
        except ValueError:
            command, arguments = msg.content, ''
        await self.command_handler.resolve(command[1:], arguments, msg, self)
