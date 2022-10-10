#!/usr/bin/env python
"""Build ParlaMint-RO corpus by converting sessions into XML format."""
import logging
from argparse import Namespace, ArgumentParser
from pathlib import Path
from typing import Generator
from framework.utils.loggingutils import configure_logging


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


def main(args):
    """Entry point of the module."""
    total, processed, failed = 0, 0, 0
    for f in iter_files(args.input_directory):
        total = total + 1
        try:
            logging.info("Converting file %s to XML.", f)
            processed = processed + 1
        except Exception as e:
            failed = failed + 1
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
