class SizeTooSmallError(Exception):
    pass


class NotLoggedInException(Exception):
    pass


class TooManyTriesError(Exception):
    pass


class LoginError(Exception):
    pass


class LogoutError(Exception):
    pass


class SubtitlesNotFoundException(Exception):
    def __init__(self, video_path):
        super().__init__(f'Subtitles not found for file: {video_path}')


class UnknownResultError(Exception):
    pass
