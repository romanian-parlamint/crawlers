#!/usr/bin/env python
"""Build ParlaMint-RO corpus by converting sessions into XML format."""
from argparse import Namespace, ArgumentParser
from ast import literal_eval
from framework.core.conversion.jsontoxml import SessionTranscriptConverter
from framework.core.conversion.namemapping import SpeakerInfo
from framework.core.conversion.namemapping import SpeakerInfoProvider
from framework.core.conversion.rootcorpusfilebuilder import RootCorpusFileBuilder
from framework.utils.loggingutils import configure_logging
from pathlib import Path
from typing import Dict
from typing import Generator
from typing import List
import logging
import pandas as pd
import sys


def iter_files(directory: str,
               max_files: int = None) -> Generator[Path, None, None]:
    """Recursively iterates over files of the specified type in a given directory.

    Parameters
    ----------
    directory: str, required
        The directory to iterate.
    max_files: int, optional
        If set, limits the iteration to its value; otherwise returns all files.

    Returns
    -------
    file_path: generator of pathlib.Path
        The generator that returns the path of each file.
    """
    root_path = Path(directory)
    if max_files is None:
        max_files = sys.maxint
    count = 0
    for file_path in root_path.glob('*.json'):
        if count < max_files:
            count += 1
            yield file_path
        else:
            break


def build_output_file_path(input_file: str, output_dir: str) -> str:
    """Build the path of the output file.

    Parameters
    ----------
    input_file: str, required
        The path of the session transcript in JSON format.
    output_dir: Path, required
        The path of the output directory.

    Returns
    -------
    output_file: str
        The path of the output file.
    """
    output_dir = Path(output_dir)
    input_file = Path(input_file)
    parts = input_file.stem.split('-')
    date = "-".join(parts[:-1])
    id = parts[-1]
    file_path = Path('ParlaMint-RO_{}-id{}.xml'.format(date, id))
    output_file = output_dir / file_path
    return str(output_file)


def read_personal_information(personal_info_file: str) -> List[SpeakerInfo]:
    """Read personal information from the specified file.

    Parameters
    ----------
    personal_info_file: str, required
        The path of the CSV file containing personal info.

    Returns
    -------
    personal_info: list of SpeakerInfo
        The personal info as a list of SpeakerInfo instances.
    """

    def is_empty(value: str) -> bool:
        return pd.isnull(value) or pd.isna(value) or len(value) == 0

    names = set()
    personal_info = []
    df = pd.read_csv(personal_info_file,
                     converters={
                         'first_name': literal_eval,
                         'last_name': literal_eval
                     })

    for row in df.itertuples():
        if row.full_name in names:
            continue
        profile_image = None if is_empty(
            row.profile_image) else row.profile_image
        item = SpeakerInfo(row.first_name,
                           row.last_name,
                           sex=row.sex,
                           profile_image=profile_image)
        personal_info.append(item)
        names.add(row.full_name)
    return personal_info


def read_name_map(file_path: str) -> Dict[str, str]:
    """Read the name map from the specified CSV file.

    Parameters
    ----------
    file_path: str, required
        The path of the CSV file containing name mapping data.

    Returns
    -------
    name_map: dict of (str,str)
        The dictionary mapping names as they appear in the transcripts to the correct names.
    """
    df = pd.read_csv(file_path)
    name_map = {row.name.lower(): row.correct_name for row in df.itertuples()}
    return name_map


def main(args):
    """Entry point of the module."""
    output_dir = Path(args.output_directory)
    output_dir.mkdir(exist_ok=True, parents=True)

    speaker_info_provider = SpeakerInfoProvider(
        read_name_map(args.speaker_name_map),
        read_personal_information(args.profile_info))

    root_file_path = str(output_dir / Path("ParlaMint-RO.xml"))
    root_builder = RootCorpusFileBuilder(root_file_path,
                                         args.corpus_root_template,
                                         speaker_info_provider)
    total, processed, failed = 0, 0, 0
    sample_size = args.sample_size if args.build_sample else None
    for f in iter_files(args.input_directory, max_files=sample_size):
        total = total + 1
        try:
            output_file = build_output_file_path(f, str(output_dir))
            converter = SessionTranscriptConverter(f, args.session_template,
                                                   speaker_info_provider,
                                                   output_file)
            converter.covert(args.build_sample)
            root_builder.add_corpus_file(output_file)
            processed = processed + 1
        except Exception as e:
            failed = failed + 1
            faulty_file = Path(output_file)
            if faulty_file.exists():
                faulty_file.unlink()
            logging.exception(
                "Failed to build session XML from %s. Exception: %r", f, e)

    logging.info("Processed: %s/%s", processed, total)
    if failed > 0:
        logging.info("Failed: %s/%s", failed, total)
    logging.info("That's all folks!")


def parse_arguments() -> Namespace:
    """Parse command-line arguments.

    Returns
    -------
    args: argparse.Namespace
        The command-line arguments.
    """
    parser = ArgumentParser(description='Build ParlaMint-RO corpus.')
    parser.add_argument(
        '-i',
        '--input-directory',
        help="The directory containing session transcripts in JSON format.",
        default='data/sessions/')
    parser.add_argument('--session-template',
                        help="The path of the session template file.",
                        default='data/templates/session-template.xml')
    parser.add_argument('--corpus-root-template',
                        help="The path of the corpus root template.",
                        default='data/templates/corpus-root-template.xml')
    parser.add_argument(
        '--speaker-name-map',
        help="The path of the CSV file mapping speaker names to correct names.",
        type=str,
        default='data/speakers/speaker-name-map.csv')
    parser.add_argument('--profile-info',
                        help="The CSV file containing profile info.",
                        default='data/speakers/profile-info.csv')
    parser.add_argument('-o',
                        '--output-directory',
                        help="The directory where to save corpus files.",
                        default="corpus")
    parser.add_argument('--sample',
                        help="When present, build sample corpus.",
                        action='store_true',
                        dest='build_sample')
    parser.add_argument('--sample-size',
                        help="The number of files to include in the sample.",
                        type=int,
                        default=10)

    parser.add_argument(
        '-l',
        '--log-level',
        help="The level of details to print when running.",
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        default='info')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    configure_logging(args.log_level)
    main(args)
