from api import API
from config import Config
from datetime import datetime, timezone
import discord, urllib.parse, pytz, locale


class CommandHandler:

    def __init__(self):
        self.api = API()
        self._functions = {
            'song': self.song,
            'next': self.next,
            'last': self.last
        }
        locale.setlocale(locale.LC_TIME, 'pl_PL')

    async def resolve(self, cmd, args, msgctx, client):
        try:
            command = self._functions[cmd]
        except KeyError:
            await msgctx.channel.send(
                '{}, nie zrozumiałam tego polecenia, upewnij się, że ono istnieje oraz, że zostało napisane poprawnie.'.format(
                    msgctx.author.mention))
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
        song_list = ''; i = 0
        for x in r['historyEntries']:
            date_played = datetime.utcfromtimestamp(x['timestamp']).replace(tzinfo=timezone.utc).astimezone(
                pytz.timezone(Config.timezone))
            song_list += '\n\\{} **{}** od **{}** o {}:{} (CEST) w {}'.format(u'\u2022', x['title'], x['artist'],
                        date_played.hour, date_played.minute, date_played.strftime('%A'))
            i += 1
        await msgctx.channel.send('{}, ostatnie pięć utworów, które zagrałam to:'.format(msgctx.author.mention) + song_list)

