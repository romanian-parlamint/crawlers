#!/usr/bin/env python
"""Crawl sessions of Romanian Lower House."""
from argparse import ArgumentParser
from argparse import ArgumentTypeError
import datetime
import logging
import requests
import re
from lxml import html


class UrlBuilder:
    """Builds URLs for requests."""

    BaseUrl = "http://www.cdep.ro"
    YearUrlTemplate = "/pls/steno/steno2015.calendar?cam=2&an={year}&idl=1"
    SessionUrlTemplate = "/pls/steno/steno2015.data?cam=2&dat={date}&idl=1"

    def __init__(self):
        """Create a new instance of the class."""
        pass

    def build_full_URL(self, path_and_query):
        """Build a full URL by appending base URL to path and query.

        Parameters
        ----------
        path_and_query: str, required
            The path and query parts of the URL.

        Returns
        -------
        URL: str,
            The full URL.
        """
        return UrlBuilder.BaseUrl + path_and_query

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
        return self.build_full_URL(path_and_query)

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
        return self.build_full_URL(path_and_query)


class SessionUrlsCrawler:
    """Crawl session URLs for a specific year."""

    SessionUrlRegex = r"\/pls\/steno\/steno2015.data\?cam=2&dat=(?P<date>\d{8})&idl=1"

    def __init__(self):
        """Create a new instance of session URLs crawler."""
        self.__url_builder = UrlBuilder()

    def crawl(self, year):
        """Crawl session URLs.

        Parameters
        ----------
        year: int, required
            The year for which to crawl session URLs.

        Returns
        -------
        dates_and_urls: iterable of tuples of (datetime, str)
            The collection of session dates and their URLS for the specified year.
        """
        url = self.__url_builder.build_URL_for_year(year)
        response = requests.get(url)
        html_root = html.fromstring(response.content)
        result = []
        for a in html_root.iterdescendants(tag='a'):
            href = a.get('href')
            match = re.search(SessionUrlsCrawler.SessionUrlRegex, href,
                              re.MULTILINE)
            if match:
                date_str = match.group('date')
                session_date = datetime.datetime.strptime(date_str, "%Y%m%d")
                session_url = self.__url_builder.build_full_URL(href)
                result.append((session_date, session_url))
        return result


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
        crawler = SessionUrlsCrawler()
        for year in args.years:
            logging.info(
                "Crawling session transcripts for year {}.".format(year))
            for date, url in crawler.crawl(year):
                print(date, url)


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
