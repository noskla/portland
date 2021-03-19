from config import Config
import discord, asyncio


class Voice:
    def __init__(self):
        self.voice_channels = {}
        self.voice_enabled = Config.voice_enabled
        self.audio_source = None
        self.song_data = {'ID': -1}
        if self.voice_enabled:
            try:
                self.audio_source = discord.FFmpegOpusAudio(source=Config.stream_url,
                                                            executable=Config.ffmpeg_executable)
            except discord.ClientException as err:
                print("Error occurred while initializing FFmpeg:", err)
                self.audio_enabled = False

    async def _get_now_playing_loop(self, api, client):
        while 1:
            now = api.playing_now()
            if self.song_data['ID'] != now['ID']:
                self.song_data = api.playing_now()
                await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,
                                                                       name="\"{}\" by {} on laspegas.us".format(
                                                                           now['title'], now['artist']),
                                                                       url="https://laspegas.us/"))
            await asyncio.sleep(15)

    def start_info_loop(self, api, client):
        asyncio.create_task(self._get_now_playing_loop(api, client))

    def restart_source(self):
        try:
            self.audio_source = discord.FFmpegOpusAudio(source=Config.stream_url, executable=Config.ffmpeg_executable)
            self.audio_enabled = True
        except discord.ClientException as err:
            print("Error occurred while initializing FFmpeg:", err)
            self.audio_enabled = False
        return self.audio_enabled
