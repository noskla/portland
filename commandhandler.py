from api import API
from voice import Voice
from config import Config
from datetime import datetime, timezone
import discord, urllib.parse, pytz, locale, asyncio


class CommandHandler:

    def __init__(self):
        self.api = API()
        self.voice = None
        self._functions = {
            'song': self.song,
            'next': self.next,
            'last': self.last,
            'now': self.now,
            'join': self.join,
            'leave': self.leave
        }
        locale.setlocale(locale.LC_TIME, 'pl_PL')

    def start_voice_info_loop(self, client):
        self.voice = Voice()
        self.voice.start_info_loop(self.api, client)

    async def resolve(self, cmd, args, msgctx, client):
        try:
            command = self._functions[cmd]
        except KeyError:
            await msgctx.channel.send(
                '{}, nie zrozumiałam tego polecenia, upewnij się, że ono istnieje oraz, że zostało napisane poprawnie.'.format(
                    msgctx.author.mention))
        # noinspection PyArgumentList
        await self._functions[cmd](args, msgctx, client)

    async def song(self, args, msgctx, client):
        if len(args) <= 0:
            return await msgctx.channel.send(
                '{}, potrzebuję ID utworu lub zapytania wyszukiwania.'.format(msgctx.author.mention))
        mode = 'exact_match' if args.isnumeric() else 'search'
        r, song = None, None
        try:
            if mode == 'exact_match':
                r = self.api.get_song(int(args))
                song = r['song']
            elif mode == 'search':
                r = self.api.find_song(args)
                song = r['songs'][0]
        except KeyError:
            return await msgctx.channel.send('{}, wystąpił błąd: {}'.format(msgctx.author.mention, r['error']))

        embed = discord.Embed(type='rich', title=song['title'],
                              url='https://youtube.com/results?search_query={}'.format(
                                  urllib.parse.quote(song['artist'] + ' - ' + song['title'])))
        embed.set_thumbnail(url='{}/song/{}/albumart'.format(self.api.url,
                                                             (args if args.isnumeric() else str(song['ID']))))
        embed.add_field(name='Album', value=song['album'] if song['album'] != 'Single' else 'Brak', inline=True)
        embed.add_field(name='Gatunek', value=song['genre'], inline=True)
        embed.add_field(name='Rok premiery', value=song['date_released'], inline=True)
        embed.set_author(name=song['artist'])
        await msgctx.channel.send(msgctx.author.mention + ',', embed=embed)

    async def next(self, args, msgctx, client):
        r = self.api.get_queue()
        try:
            song = r['songs'][0]
        except KeyError:
            return await msgctx.channel.send('{}, wystąpił błąd: {}'.format(msgctx.author.mention, r['error']))
        if song['album'] == 'Single':
            await msgctx.channel.send('{}, następny zagramy singiel pt. **{}** od **{}** *(ID: {})*'.format(
                msgctx.author.mention, song['title'], song['artist'], str(song['ID']))
                                      + '\nSłuchaj na <https://laspegas.us/> lub zaproś mnie na kanał głosowy!')
        else:
            await msgctx.channel.send('{}, następną zagramy **{}** od **{}** z albumu **{}** *(ID: {})*'.format(
                msgctx.author.mention, song['title'], song['artist'], song['album'], str(song['ID']))
                                      + '\nSłuchaj na <https://laspegas.us/> lub zaproś mnie na kanał głosowy!')

    async def last(self, args, msgctx, client):
        r = self.api.history()
        if r['status'] == 'Err':
            return await msgctx.channel.send('{}, wystąpił błąd: {}'.format(msgctx.author.mention, r['error']))
        song_list = '';
        i = 0
        for x in r['historyEntries']:
            date_played = datetime.utcfromtimestamp(x['timestamp']).replace(tzinfo=timezone.utc).astimezone(
                pytz.timezone(Config.timezone))
            song_list += '\n\\{} **{}** od **{}** o {}:{} (CEST) w {}'.format(u'\u2022', x['title'], x['artist'],
                                                                              date_played.hour, date_played.minute,
                                                                              date_played.strftime('%A'))
            i += 1
        await msgctx.channel.send(
            '{}, ostatnie pięć utworów, które zagrałam to:'.format(msgctx.author.mention) + song_list)

    async def now(self, args, msgctx, client):
        r = self.api.playing_now()
        if r['status'] != 'ok':
            return await msgctx.channel.send('{}, wystąpił błąd: {}'.format(msgctx.author.mention, r['error']))
        embed = discord.Embed(type='rich', title=r['title'], url='https://laspegas.us/portland')
        embed.set_thumbnail(url='{}/song/{}/albumart'.format(self.api.url, str(r['ID'])))
        embed.add_field(name='Album', value=r['album'] if r['album'] != 'Single' else 'Brak', inline=True)
        embed.add_field(name='Gatunek', value=r['genre'], inline=True)
        embed.add_field(name='Rok premiery', value=r['release_date'], inline=True)
        embed.set_author(name=r['artist'])
        await msgctx.channel.send(msgctx.author.mention + ', teraz nadajemy:', embed=embed)

    async def join(self, args, msgctx, client):
        if msgctx.author.voice is None:
            return await msgctx.channel.send('{}, najpierw dołącz na kanał głosowy, na którym powinnam grać.'.format(
                msgctx.author.mention))
        if msgctx.author.voice.channel.user_limit <= len(msgctx.author.voice.channel.members):
            return await msgctx.channel.send(
                '{}, kanał głosowy, na którym się znajdujesz jest pełny i nie mogę dołączyć.'.format(
                    msgctx.author.mention))
        if not self.voice.voice_enabled:
            return await msgctx.channel.send('{}, wsparcie dla kanałów głosowych jest wyłączone.'.format(
                msgctx.author.mention))
        try:
            await self.leave(args, msgctx, client, False)
        except KeyError:
            pass

        try:
            await msgctx.channel.send('{}, łączę się z {}...'.format(msgctx.author.mention,
                                                                     msgctx.author.voice.channel.name))
            self.voice.voice_channels[msgctx.guild.id] = await msgctx.author.voice.channel.connect(timeout=120,
                                                                                                   reconnect=True)
        except asyncio.TimeoutError as err:
            print("Error connecting to the voice channel: ", err)
            return await msgctx.channel.send(
                '{}, wystąpił błąd z łącznością z kanałem głosowym. Poinformuj administratora.'.format(
                    msgctx.author.mention))
        except discord.ClientException as err:
            print("Error connecting to the voice channel: ", err)
            await self.leave(args, msgctx, client, False)
            return await msgctx.channel.send(
                '{}, błąd: według mnie nie jestem połączona z kanałem, ale Discord myśli,' +
                ' że jestem? Spróbuj ponownie za chwilę, lub poinformuj administratora.'.format(
                    msgctx.author.mention))
        if self.voice.audio_source is None:
            await msgctx.channel.send('{}, źródło jest niedostępne.'.format(msgctx.author.mention))
            await self.leave(args, msgctx, client, False)
            return

        if not self.voice.voice_channels[msgctx.guild.id].is_playing():
            self.voice.voice_channels[msgctx.guild.id].play(self.voice.audio_source)

    async def leave(self, args, msgctx, client, send_message=True):
        self.voice.voice_channels[msgctx.guild.id].stop()
        await self.voice.voice_channels[msgctx.guild.id].disconnect()
        self.voice.voice_channels[msgctx.guild.id].cleanup()
        self.voice.voice_channels.pop(msgctx.guild.id)
        self.voice.restart_source()
        if send_message:
            await msgctx.channel.send('{}, ok, wychodzę z kanału...'.format(msgctx.author.mention))
