#!/usr/bin/env python
"""Crawl deputy data."""
import argparse
import logging
import pandas as pd
from framework.utils.loggingutils import configure_logging
from framework.utils.sessionutils import load_speakers
from framework.core.crawling.memberprofile import MemberProfileCrawler
from framework.utils.dataframeutils import save_data_frame


def main(args):
    """Crawl deputy data from session transcriptions.

    Parameters
    ----------
    args: argparse.Namespace, required
        The command-line arguments of the script.
    """
    data = {}
    for s in load_speakers(args.sessions_dir):
        profile_url = s['profile_url']
        if profile_url not in data:
            data[profile_url] = s['sex']
    records = []
    for profile_url, sex in data.items():
        crawler = MemberProfileCrawler()
        profile_info = crawler.crawl(profile_url)
        profile_info.update({'profile_url': profile_url, 'sex': sex})
        records.append(profile_info)
        break
    save_data_frame(pd.DataFrame.from_records(records), args.profile_info_file)
    logging.info("That's all folks!")


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Crawl deputy data from session transcriptions.')
    parser.add_argument(
        '--sessions-dir',
        help="The path of the directory containing crawled sessions.",
        type=str,
        default="./data/sessions/")
    parser.add_argument('--profile-info-file',
                        help="The path of the CSV file where to save data.",
                        type=str,
                        default="./data/speakers/profile-info.csv")
    parser.add_argument(
        '-l',
        '--log-level',
        help="The level of details to print when running.",
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        default='info')
    parser.add_argument('--log-file',
                        help="""
                        Specifies the file where to log messages.
                        If not provided the log messages will be saved only to console.
                        """,
                        default=None)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    configure_logging(args.log_level, args.log_file)
    main(args)
