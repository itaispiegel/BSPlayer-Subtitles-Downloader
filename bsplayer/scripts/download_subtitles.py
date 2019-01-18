import glob
import sys

import click

from bsplayer import BSPlayer
from bsplayer.exceptions import SubtitlesNotFoundException, TooManyTriesError


@click.command()
@click.argument('video_path_glob')
@click.option('-d', '--dest-directory', help='The directory to download the subtitles to')
@click.option('-l', '--language', help='The language(s) in which to download subtitles (three-letter, comma-separated like "pol,eng")')
@click.option('-t', '--timeout', help='Timeout for downloading each file', default=5.0, type=float)
@click.option('-T', '--tries', help='Amount of tries to the try the request against the server', default=5, type=int)
@click.option('-v', '--verbose', help='Verbose output', is_flag=True, default=False)
@click.option('-W', '--no-wildcard', help="Don't treat the video path as a wildcard", is_flag=True)
def download(video_path_glob, dest_directory, language, timeout, tries, verbose, no_wildcard):
    video_files = [video_path_glob]
    if not no_wildcard:
        video_files = glob.glob(video_path_glob)
    if not video_files:
        sys.exit('ERROR: No files matched')
    if not language:
        language = 'eng,eng'

    try:
        with BSPlayer(timeout=timeout, tries=tries, verbose=verbose) as bsplayer:
            for video_path in video_files:
                bsplayer.download_by_path(video_path, dest_directory, language_ids=language)
    except SubtitlesNotFoundException:
        print(f'ERROR: Subtitles not found for {video_path}', file=sys.stderr)
    except TooManyTriesError:
        print(f'ERROR: Request failed - too many tries', file=sys.stderr)


if __name__ == '__main__':
    download()
