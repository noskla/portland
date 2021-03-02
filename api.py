from config import Config
import requests, sys


class API:

    def __init__(self):
        self.url = Config.api_url
        if self.get_songs()['status'] == 'Err':
            sys.exit('API test failed ({}/songs?page=0)'.format(self.url))
        else:
            print('API test successful')

    def get_songs(self, page=1):
        r = requests.get('{}/songs?page={}'.format(self.url, page))
        if r.status_code != 200:
            return {'status': 'Err', 'error': r.text}
        try:
            return r.json()
        except ValueError:
            return {'status': 'Err', 'error': r.text}
