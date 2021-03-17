from api import API
from config import Config
import discord


class Voice:
    def __init__(self):
        self.voice_channels = {}
        self.voice_enabled = Config.voice_enabled
        self.audio_source = None
        if self.voice_enabled:
            try:
                self.audio_source = discord.FFmpegOpusAudio(source=Config.stream_url, executable=Config.ffmpeg_executable)
            except discord.ClientException as err:
                print("Error occurred while initializing FFmpeg:", err)
                self.audio_enabled = False

    def restart_source(self):
        try:
            self.audio_source = discord.FFmpegOpusAudio(source=Config.stream_url, executable=Config.ffmpeg_executable)
            self.audio_enabled = True
        except discord.ClientException as err:
            print("Error occurred while initializing FFmpeg:", err)
            self.audio_enabled = False
        return self.audio_enabled

