#!/usr/bin/env python
"""Filters the speakers of crawled sessions into Parliament members and guests."""
from argparse import ArgumentParser
import logging
import pandas as pd
from framework.utils.loggingutils import configure_logging
from framework.utils.sessionutils import load_speakers
from framework.utils.dataframeutils import save_data_frame


def is_guest(speaker):
    """Determine whether the provided speaker is a guest or a member of the Parliament.

    Parameters
    ----------
    speaker: dict, required
        The speaker.

    Returns
    -------
    is_guest: bool
        True if the speaker is a guest; False if the speaker is a member of the Parliament.
    """
    profile_url = speaker['profile_url']
    return profile_url is None or len(profile_url) == 0


def main(args):
    """Filter speakers into Parliament members and guests."""
    guests, members = {}, {}
    for speaker in load_speakers(args.sessions_dir):
        speaker_name = speaker['full_name']
        guest_speaker = is_guest(speaker)
        if guest_speaker and speaker_name not in guests:
            guests[speaker_name] = speaker
        if (not guest_speaker) and (speaker_name not in members):
            members[speaker_name] = speaker

    guests = list(guests.values())
    members = list(members.values())
    save_data_frame(pd.DataFrame.from_records(guests), args.guests_file)
    save_data_frame(pd.DataFrame.from_records(members), args.members_file)
    logging.info("That's all folks!")


def parse_arguments():
    """Parse the command-line arguments.

    Returns
    -------
    args: argparse.Namespace
        The command-line arguments.
    """
    parser = ArgumentParser(description='Filter speakers of crawled sessions.')
    parser.add_argument(
        '--sessions-dir',
        help="The path of the directory containing crawled sessions.",
        type=str,
        default="./data/sessions/")
    parser.add_argument(
        '--save-members-to',
        help="The path of the output CSV file containing speakers.",
        type=str,
        dest='members_file',
        default="./data/speakers/parliament-members.csv")
    parser.add_argument(
        '--save-guests-to',
        help="The path of the output CSV file containing speakers.",
        type=str,
        dest='guests_file',
        default="./data/speakers/guest-speakers.csv")
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
