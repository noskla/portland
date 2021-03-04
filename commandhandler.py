from api import API
import discord, urllib.parse


class CommandHandler:

    def __init__(self):
        self.api = API()
        self._functions = {
            'song': self.song
        }

    async def resolve(self, cmd, args, msgctx, client):
        try:
            await self._functions[cmd](args, msgctx, client)
        except KeyError:
            await msgctx.channel.send(
                '{}, nie zrozumiałam tego polecenia, upewnij się, że ono istnieje oraz, że zostało napisane poprawnie.'.format(
                    msgctx.author.mention))

    async def song(self, args, msgctx, client):
        if len(args) <= 0:
            await msgctx.channel.send(
                '{}, potrzebuję ID utworu lub zapytania wyszukiwania.'.format(msgctx.author.mention))
            return
        mode = 'exact_match' if args.isnumeric() else 'search'
        r, song = None, None
        if mode == 'exact_match':
            r = self.api.get_song(int(args)); song = r['song']
        elif mode == 'search':
            r = self.api.find_song(args); song = r['songs'][0]

        if r['status'] == 'error':
            await msgctx.channel.send('{}, wystąpił błąd: {}'.format(msgctx.author.mention, r['text']))
            return

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
