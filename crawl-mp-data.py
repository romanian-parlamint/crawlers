#!/usr/bin/env python
"""Crawl deputy data."""
import argparse
import logging
import pandas as pd
from pathlib import Path
from framework.utils.loggingutils import configure_logging
from framework.utils.sessionutils import load_speakers
from framework.core.crawling.memberprofile import MemberProfileCrawler
from framework.utils.dataframeutils import save_data_frame


def load_processed_urls(profile_data_file: str) -> set:
    """Load the already processed URLs from the profile data file.

    Parameters
    ----------
    profile_data_file: str, required
        The path to the CSV file containing already scrapped profile data.

    Returns
    -------
    processed_urls: iterable of str
        The set of processed profile URLs.
    """
    profiles_file = Path(profile_data_file)
    if not profiles_file.exists():
        return set()

    df = pd.read_csv(profile_data_file)
    return set(df.profile_url)


def load_profile_data(sessions_dir: str, exclude_urls: set = None) -> dict:
    """Scan the session transcripts for profile URLs and returns URLs that are not in the excluded list.

    Parameters
    ----------
    sessions_dir: str, required
        The path of the directory containing session transcriptions.
    exclude_urls: set of str, optional
        The URLs to exclude.

    Returns
    -------
    profile_data: dict
        A dictionary containing profile URLs as keys and MP sex as values.
    """
    logging.info("Searching profile URLs in session transcripts from %s.",
                 sessions_dir)
    if exclude_urls is None:
        exclude_urls = set()
    profile_data = {}
    for s in load_speakers(args.sessions_dir):
        profile_url = s['profile_url']
        if profile_url is None:
            continue
        profile_url = profile_url.rstrip('.')
        if profile_url not in exclude_urls:
            profile_data[profile_url] = s['sex']
            exclude_urls.add(profile_url)
    return profile_data


def main(args):
    """Crawl deputy data from session transcriptions.

    Parameters
    ----------
    args: argparse.Namespace, required
        The command-line arguments of the script.
    """
    exclude_urls = load_processed_urls(args.profile_info_file)
    data = load_profile_data(args.sessions_dir, exclude_urls=exclude_urls)
    logging.info("Start crawling profile info.")
    records = []
    crawler = MemberProfileCrawler()
    for profile_url, sex in data.items():
        try:
            logging.info("Crawling profile info for URL %s.", profile_url)
            profile_info = crawler.crawl(profile_url)
            profile_info.update({'profile_url': profile_url, 'sex': sex})
            records.append(profile_info)
        except Exception as e:
            logging.error("Could not crawl session contents from URL %s.",
                          profile_url,
                          exc_info=e)

    logging.info("Saving profile data to %s.", args.profile_info_file)
    save_data_frame(pd.DataFrame.from_records(records),
                    args.profile_info_file,
                    append=True)
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
