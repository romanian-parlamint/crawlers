#!/usr/bin/env python
"""Crawl sessions of Romanian Lower House."""
from argparse import ArgumentParser
from argparse import ArgumentTypeError
import datetime
import logging
from core.navigation import UrlBuilder
from core.crawling import SessionUrlsCrawler
from core.crawling import SessionSummaryCrawler
from pprint import pprint
import json


def iter_session_URLs(args):
    """Iterate over session URLs from the arguments.

    Parameters
    ----------
    args: argparse.Namespace, required
        The command-line arguments of the script.

    Returns
    -------
    url_generator: generator of (datetime, str) tuples
        The collection of session dates and their URLs.
    """
    if args.date:
        url_builder = UrlBuilder()
        yield args.date, url_builder.build_URL_for_session(args.date)
    else:
        crawler = SessionUrlsCrawler()
        for year in args.years:
            for date, url in crawler.crawl(year):
                yield date, url


def main(args):
    """Crawl session transcripts."""
    if args.date:
        logging.info("Crawling session transcript for date {}.".format(
            args.date))
    else:
        logging.info("Crawling sessions for the following years: {}.".format(
            ", ".join([str(year) for year in args.years])))
    for date, url in iter_session_URLs(args):
        data = SessionSummaryCrawler().crawl(url)
        with open("{}.json".format(date.strftime("%Y-%m-%d")),
                  'w',
                  encoding='utf8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def valid_year(year):
    """Return True if provided year is valid as an argument to the script.

    Parameters
    ----------
    year: str, required
        The year to validate.
    """
    year = int(year)
    max_year = datetime.date.year
    if year < 2000 or year > max_year:
        raise ArgumentTypeError(
            "Year must be betweer 2000 and {} inclusive.".format(max_year))
    return year


def parse_arguments():
    """Parse command-line arguments."""
    parser = ArgumentParser(
        description='Crawl sessions of Romanian Lower House')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--date',
        help="The ISO-format date for which to crawl session transcript.",
        type=datetime.date.fromisoformat)
    group.add_argument('--year',
                       help="List of years for which to crawl transcripts.",
                       dest='years',
                       type=int,
                       choices=range(1999,
                                     datetime.date.today().year + 1),
                       nargs='+')
    parser.add_argument(
        '-l',
        '--log-level',
        help="The level of details to print when running.",
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        default='info')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=getattr(logging, args.log_level.upper()))
    main(args)
    logging.info("That's all folks!")
