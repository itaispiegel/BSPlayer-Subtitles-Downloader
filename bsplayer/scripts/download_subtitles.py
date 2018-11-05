import glob
import sys

import click

from bsplayer import BSPlayer
from bsplayer.exceptions import SubtitlesNotFoundException


@click.command()
@click.argument('video_path_glob')
@click.option('-d', '--dest-directory', help='The directory to download the subtitles to')
@click.option('-t', '--timeout', help='Timeout for downloading each file', type=float)
@click.option('-v', '--verbose', help='Verbose output', is_flag=True, default=False)
def download(video_path_glob, dest_directory, timeout, verbose):
    video_files = glob.glob(video_path_glob)
    if not video_files:
        sys.exit('ERROR: No files matched')

    for video_path in video_files:
        with BSPlayer(timeout=timeout, verbose=verbose) as bsplayer:
            try:
                bsplayer.download_by_path(video_path, dest_directory)
            except SubtitlesNotFoundException:
                print(f'ERROR: Subtitles not found for {video_path}', file=sys.stderr)


if __name__ == '__main__':
    download()
