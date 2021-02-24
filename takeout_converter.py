import argparse
import csv
from dataclasses import dataclass
from typing import List, Dict
from logging import getLogger
from pathlib import Path


logger = getLogger(__name__)


@dataclass
class SongRecord:
    title: str
    album: str
    artist: str
    duration_ms: int
    rating: int
    play_count: int
    removed: bool

    def __post_init__(self):
        self.duration_ms = int(self.duration_ms)
        self.rating = int(self.rating)
        self.play_count = int(self.play_count)
        self.removed = bool(self.removed)  # TODO:: don't actually know what this is other than empty

    def __str__(self):
        return ','.join([
            self.title,
            self.album,
            self.artist,
            str(self.duration_ms),
            str(self.rating),
            str(self.play_count),
            str(self.removed) if self.removed else ''])


def fuse_main_csv(full_path: Path) -> List[Dict[str, str]]:
    csv_filenames = full_path.glob('*.csv')
    lines = []
    for csv_filename in csv_filenames:
        with open(csv_filename.absolute(), 'r') as csv_in:
            reader = csv.DictReader(
                csv_in,
                fieldnames=['title', 'album', 'artist', 'duration_ms', 'rating', 'play_count', 'removed'],
            )
            next(reader, None)
            lines.extend([SongRecord(**line) for line in reader])
    return lines

def output_main_csv(main_csv: List[SongRecord], full_path: Path):
    {'Title': '05 - I Shot The Sheriff.mp3',
     'Album': 'Burnin&#39;',
     'Artist': 'Bob Marley',
     'Duration (ms)': '282000',
     'Rating': '0',
     'Play Count': '0',
     'Removed': ''}
    with open('main_csv.csv', 'w') as outfile:
        header = ['Title,Album,Artist,Duration (ms),Rating,Play Count,Removed']
        lines = '\n'.join(header + [str(line) for line in main_csv])
        outfile.writelines(lines)


def move_audio_files(full_path: Path, main_csv):
    pass


def copy_audio_files(full_path: Path, main_csv):
    pass


def main():
    parser = argparse.ArgumentParser(description='Convert google music takeout results to plex-friendly structure')
    parser.add_argument(
        'takeout-tracks-directory',
        type=str,
        nargs='?',
        default='testfiles',
        help='The full path to the directory containing the flat list of tracks and corresponding csv files.',
    )
    parser.add_argument(
        'dry-run',
        type=bool,
        default=False,
        nargs='?',
        help='Prevent the renaming, removal, or creation of any actual audio files. Will still output the combined CSV file for manul confirmation',
    )
    parser.add_argument(
        'move-files',
        type=bool,
        default=False,
        nargs='?',
        help='In order to save space during operation, actually move files instead of copying them. If something goes wrong during the command, rolling back will not be possible.'
    )
    parser.add_argument(
        'main-csv',
        type=str,
        default='',
        nargs='?',
        help='Specify the google takeout csv file to use for operating on audio files. This can be generated by running with dry-run first. Specifying it will skip the csv file scrape step.',
    )
    args = vars(parser.parse_args())

    # Validate tracks directory is actually a directory.
    full_path = Path(args['takeout-tracks-directory'])
    if not full_path.is_dir():
        logger.error('Takeout tracks directory must be a directory. %s is not a directory.', str(full_path.absolute()))
        return

    # Validate the main csv is actually a file if it was specified
    main_csv = Path(args['main-csv']) if args.get('main-csv') else None
    use_main_csv = False
    if main_csv:
        if main_csv.is_file():
            use_main_csv = True
        else:
            logger.error('Main CSV file must be a csv file. %s is not a csv file.', str(main_csv.absolute()))
            return

    if not use_main_csv:
        main_csv = fuse_main_csv(full_path)
        output_main_csv(main_csv, full_path)

    if not args.get('dry_run'):
        if args.get('move_files'):
            move_audio_files(full_path, main_csv)
        else:
            copy_audio_files(full_path, main_csv)

if __name__ == "__main__":
    main()
