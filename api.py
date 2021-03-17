from config import Config
import requests, sys, urllib.parse


def _check_errors(response):
    if response.status_code != 200:
        return {'status': 'Err', 'error': response.text}
    try:
        return response.json()
    except ValueError:
        return {'status': 'Err', 'error': response.text}


class API:

    def __init__(self):
        self.url = Config.api_url
        if self.get_songs()['status'] == 'Err':
            sys.exit('API test failed ({}/songs?page=0)'.format(self.url))
        else:
            print('API test successful')

    # -- -- --

    def get_songs(self, page=1):
        r = requests.get('{}/songs?page={}'.format(self.url, page))
        return _check_errors(r)

    def get_song(self, song_id):
        r = requests.get('{}/song/{}'.format(self.url, str(song_id)))
        return _check_errors(r)

    def find_song(self, search_query):
        r = requests.get('{}/song/search?query={}'.format(self.url, urllib.parse.quote(search_query)))
        return _check_errors(r)

    def get_queue(self):
        r = requests.get('{}/queue'.format(self.url))
        return _check_errors(r)

    def history(self):
        r = requests.get('{}/history?limit=5'.format(self.url))
        return _check_errors(r)

    def playing_now(self):
        r = requests.get('{}/now'.format(self.url))
        return _check_errors(r)