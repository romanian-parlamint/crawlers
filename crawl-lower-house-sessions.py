#!/usr/bin/env python
"""Crawl sessions of Romanian Lower House."""
from argparse import ArgumentParser
from argparse import ArgumentTypeError
import datetime
import logging


class UrlBuilder:
    """Builds URLs for requests."""

    BaseUrl = "http://www.cdep.ro"
    YearUrlTemplate = "/pls/steno/steno2015.calendar?cam=2&an={year}&idl=1"
    SessionUrlTemplate = "/pls/steno/steno2015.data?cam=2&dat={date}&idl=1"

    def __init__(self):
        """Create a new instance of the class."""
        pass

    @classmethod
    def build_URL_for_year(self, year):
        """Build URL for retrieving the calendar of sessions.

        Parameters
        ----------
        year: int, required
            The year for which to build the URL.

        Returns
        -------
        URL: str
            The URL of the page containing the calendar of sessions for the specified year.
        """
        path_and_query = UrlBuilder.YearUrlTemplate.format(year=year)
        return UrlBuilder.BaseUrl + path_and_query

    def build_URL_for_session(self, session_date):
        """Build URL for a session that took place on the specified date.

        Parameters
        ----------
        session_date: datetime.date, required
            The date of the session.

        Returns
        -------
        URL: str
            The URL of the session transcript for the provided date.
        """
        date_string = session_date.strftime("%Y%m%d")
        path_and_query = UrlBuilder.SessionUrlTemplate.format(date=date_string)
        return UrlBuilder.BaseUrl + path_and_query


def main(args):
    """Crawl session transcripts."""
    url_builder = UrlBuilder()
    if args.date:
        logging.info("Crawling session transcript for date {}.".format(
            args.date))
        session_url = url_builder.build_URL_for_session(args.date)
        logging.info(
            "The URL of the session transcript is {}.".format(session_url))
    else:
        for year in args.years:
            logging.info(
                "Crawling session transcripts for year {}.".format(year))


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
