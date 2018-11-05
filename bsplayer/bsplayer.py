import os
import random
import sys
from xml.etree import ElementTree

import logbook
import requests

from bsplayer.exceptions import NotLoggedInException, TooManyTriesError, LoginError, LogoutError, \
    SubtitlesNotFoundException, UnknownResultError, SizeTooSmallError
from bsplayer.subtitles import Subtitle, SubtitleResults
from bsplayer.videos import VideoInfo


class BSPlayerDecorators:
    @classmethod
    def requires_login(cls, func):
        def wrapped(self, *args, **kwargs):
            if not self.token:
                raise NotLoggedInException('You need to be authenticated to perform this action')
            return func(self, *args, **kwargs)

        return wrapped


class BSPlayer:
    # s1-9, s101-109
    SUB_DOMAINS = ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9',
                   's101', 's102', 's103', 's104', 's105', 's106', 's107', 's108', 's109']
    API_URL_TEMPLATE = "http://{sub_domain}.api.bsplayer-subtitles.com/v1.php"

    HEADERS = {
        'User-Agent': 'BSPlayer/2.x (1022.12362)',
        'Content-Type': 'text/xml; charset=utf-8',
        'Connection': 'close',
    }

    DATA_FORMAT = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                   '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" '
                   'xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" '
                   'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                   'xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
                   'xmlns:ns1="{search_url}">'
                   '<SOAP-ENV:Body SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
                   '<ns1:{func_name}>{params}</ns1:{func_name}></SOAP-ENV:Body></SOAP-ENV:Envelope>')

    APP_ID = 'BSPlayer v2.67'

    SUBS_DIRECTORY_NAME = "Subs"

    @classmethod
    def get_sub_domain(cls):
        sub_domain = random.choice(cls.SUB_DOMAINS)
        return cls.API_URL_TEMPLATE.format(sub_domain=sub_domain)

    def __init__(self, search_url=None, timeout=5.0, verbose=False):
        self.search_url = search_url or self.get_sub_domain()
        self.token = None
        self.logger = logbook.Logger('BSPlayerLogger')
        self.timeout = timeout

        if verbose:
            self.logger.handlers.append(logbook.StreamHandler(sys.stdout))

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.logout()

    def api_request(self, func_name, params='', tries=5):
        soap_action_header = f'"http://api.bsplayer-subtitles.com/v1.php#{func_name}"'
        headers = self.HEADERS.copy()
        headers['SOAPAction'] = soap_action_header

        data = self.DATA_FORMAT.format(search_url=self.search_url, func_name=func_name, params=params)

        self.logger.info(f'Sending request: {func_name}')
        for i in range(tries):
            try:
                self.logger.info(f'Try number {i} for operation {func_name}')
                res = requests.post(self.search_url, data=data, headers=headers, timeout=self.timeout)
                return ElementTree.fromstring(res.content)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, TimeoutError, ConnectionError):
                self.logger.exception()

        self.logger.error(f'Too many tries {tries}')
        raise TooManyTriesError(func_name)

    def login(self):
        if self.token:
            self.logger.info('Already logged in')
            return

        root = self.api_request(func_name='logIn',
                                params=('<username></username>'
                                        '<password></password>'
                                        f'<AppId>{self.APP_ID}</AppId>'))
        res = root.find('.//return')
        if res.find('status').text == 'OK':
            self.token = res.find('data').text
            self.logger.info('Logged in successfully')
            return

        self.logger.error('Error logging in')
        raise LoginError()

    def logout(self):
        if not self.token:
            self.logger.info('Already logged out')
            return

        root = self.api_request(func_name='logOut', params=f'<handle>{self.token}</handle>')
        res = root.find('.//return')
        if res.find('status').text == 'OK':
            self.logger.info('Logged out successfully')
            self.token = None
            return

        self.logger.error('Error logging out')
        raise LogoutError()

    @BSPlayerDecorators.requires_login
    def search_subtitles(self, video_path, language_ids='eng,eng'):
        if isinstance(language_ids, (list, tuple, set)):
            language_ids = ','.join(language_ids)

        try:
            video_info = VideoInfo(video_path)
            self.logger.info(
                f'Searching for subtitles of path={video_path} size={video_info.size} hash={video_info.hash}')
            root = self.api_request(func_name='searchSubtitles', params=(
                f'<handle>{self.token}</handle>'
                f'<movieHash>{video_info.hash}</movieHash>'
                f'<languageId>{language_ids}</languageId>'
                f'<imdbId>*</imdbId>'
            ))

            res = root.find('.//return/result')
            if res.find('status').text == 'Not found':
                raise SubtitlesNotFoundException(video_path)
            elif res.find('status').text != 'OK':
                raise UnknownResultError()

            items = root.findall('.//return/data/item')
            subtitles = []
            if items:
                self.logger.info('Subtitles found')
                for item in items:
                    subtitles.append(Subtitle.from_element_tree(item))

            return SubtitleResults(subtitles)
        except SizeTooSmallError:
            self.logger.exception('Probably not a video file')
            raise SubtitlesNotFoundException(video_path)

    @BSPlayerDecorators.requires_login
    def download_by_path(self, video_path, dest_directory=None, language_ids='eng,eng'):
        if dest_directory is None:
            dest_directory = os.path.join(os.path.dirname(video_path))
        self.logger.info(f'Downloading subtitles for file {video_path}, storing at directory {dest_directory}')

        subtitles = self.search_subtitles(video_path, language_ids)
        return subtitles.sort_by_rating()[0].download(dest_directory)
