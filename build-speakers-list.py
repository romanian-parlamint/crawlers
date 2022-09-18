#!/usr/bin/env python
"""Builds an unique list of speaker names from scrapped sessions."""
import argparse
import logging
import pandas as pd
from framework.utils.loggingutils import configure_logging
from framework.utils.sessionutils import load_speakers
from framework.utils.dataframeutils import save_data_frame


def main(args):
    """Build a list of unique speaker names."""
    speaker_names = set()
    for speaker in load_speakers(args.sessions_dir):
        name = speaker['full_name']
        speaker_names.add(name)
    records = [{'name': name, 'correct_name': ''} for name in speaker_names]
    save_data_frame(pd.DataFrame.from_records(records), args.names_list)
    logging.info("That's all folks!")


def parse_arguments():
    """Parse the command-line arguments.

    Returns
    -------
    args: argparse.Namespace
        The command-line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--sessions-dir',
        help="The path of the directory containing crawled sessions.",
        type=str,
        default="./data/sessions/")
    parser.add_argument(
        '--names-list',
        help="The path of the CSV file where to save the list of unique names.",
        type=str,
        default="./data/speakers/speaker-names.csv")
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
