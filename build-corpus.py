#!/usr/bin/env python
"""Build ParlaMint-RO corpus by converting sessions into XML format."""
import logging
from argparse import Namespace, ArgumentParser
from pathlib import Path
from typing import Generator
from framework.utils.loggingutils import configure_logging
from framework.core.conversion.jsontoxml import SessionTranscriptConverter
import pandas as pd


def iter_files(directory: str) -> Generator[Path, None, None]:
    """Recursively iterates over files of the specified type in a given directory.

    Parameters
    ----------
    directory: str, required
        The directory to iterate.

    Returns
    -------
    file_path: generator of pathlib.Path
        The generator that returns the path of each file.
    """
    root_path = Path(directory)
    for file_path in root_path.glob('*.json'):
        yield file_path
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
    file_path = Path('ParlaMint-RO-{}.xml'.format(input_file.stem))
    output_file = output_dir / file_path
    return str(output_file)


def main(args):
    """Entry point of the module."""
    output_dir = Path(args.output_directory)
    output_dir.mkdir(exist_ok=True, parents=True)
    df = pd.read_csv(args.speaker_name_map)
    name_map = {row.name.lower(): row.correct_name for row in df.itertuples()}

    # TODO: Initialize corpus root builder
    total, processed, failed = 0, 0, 0
    for f in iter_files(args.input_directory):
        total = total + 1
        try:
            # TODO: Build the output file path
            output_file = build_output_file_path(f, args.output_directory)
            converter = SessionTranscriptConverter(f, args.session_template,
                                                   name_map, output_file)
            converter.covert()
            # TODO: Add the output file to corpus root
            processed = processed + 1
        except Exception as e:
            failed = failed + 1
            # TODO: Check if output file exists and delete it
            logging.exception(
                "Failed to build session XML from %s. Exception: %r", f, e)

    logging.info("Processed: %s/%s", processed, total)
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
    parser.add_argument(
        '--speaker-name-map',
        help="The path of the CSV file mapping speaker names to correct names.",
        type=str,
        default='data/speakers/speaker-name-map.csv')
    parser.add_argument('-o',
                        '--output-directory',
                        help="The directory where to save corpus files.",
                        default="corpus")

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
