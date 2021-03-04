from api import API
import discord, urllib.parse


class CommandHandler:

    def __init__(self):
        self.api = API()
        self._functions = {
            'song': self.song
        }

    async def resolve(self, cmd, args, msgctx, client):
        await self._functions[cmd](args, msgctx, client)

    async def song(self, args, msgctx, client):
        if len(args) <= 0:
            await msgctx.channel.send(
                '{}, potrzebuję ID utworu lub zapytania wyszukiwania.'.format(msgctx.author.mention))
            return
        song_id = args
        mode = 'exact_match' if song_id.isnumeric() else 'search'
        r, song = None, None
        if mode == 'exact_match':
            r = self.api.get_song(int(song_id))
            song = r['song']
        elif mode == 'search':
            r = self.api.find_song(song_id)
            song = r['songs'][0]

        if r['status'] == 'error':
            await msgctx.channel.send('{}, wystąpił błąd: {}'.format(msgctx.author.mention, r['text']))
            return

        embed = discord.Embed(type='rich', title=song['title'],
                              url='https://youtube.com/results?search_query={}'.format(
                                  urllib.parse.quote(song['artist'] + ' - ' + song['title'])))
        embed.set_thumbnail(url='{}/song/{}/albumart'.format(self.api.url,
                                                             (song_id if song_id.isnumeric() else str(song['ID']))))
        embed.add_field(name='Album', value=song['album'] if song['album'] != 'Single' else 'Brak', inline=True)
        embed.add_field(name='Gatunek', value=song['genre'], inline=True)
        embed.add_field(name='Rok premiery', value=song['date_released'], inline=True)
        embed.set_author(name=song['artist'])
        await msgctx.channel.send(msgctx.author.mention + ',', embed=embed)
