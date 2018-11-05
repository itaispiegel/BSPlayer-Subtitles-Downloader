import gzip
import io
import os

import requests

from bsplayer.xml import ElementTreeObject


class Subtitle(ElementTreeObject):
    __properties__ = {'subID': 'id', 'subSize': 'size', 'subDownloadLink': 'url', 'subLang': 'language',
                      'subName': 'name', 'subFormat': 'format', 'subHash': 'hash', 'subRating': 'rating'}
    __types__ = {'size': int, 'rating': int}
    __repr_format__ = '<{name}: {language} ({rating})>'

    def download(self, directory):
        if directory is None:
            raise TypeError("You didn't specify the destination directory")

        headers = {'User-Agent': 'Mozilla/4.0 (compatible; Synapse)', 'Content-Length': '0'}
        res = requests.get(self.url, headers=headers)

        if res.content == '500':
            raise Exception('Error while downloading subtitles')

        with gzip.GzipFile(fileobj=io.BytesIO(res.content)) as gf:
            with open(os.path.join(directory, self.name), 'wb') as f:
                f.write(gf.read())

        return True


class SubtitleResults:
    def __init__(self, subtitles):
        self.subtitles = subtitles

    def sort_by_rating(self):
        return sorted(self.subtitles, key=lambda s: s.rating, reverse=True)

    def __len__(self):
        return len(self.size)

    def __getitem__(self, item):
        return self.subtitles[item]

    def __repr__(self):
        return f'<{self.__class__.__name__}: {len(self)}>'
