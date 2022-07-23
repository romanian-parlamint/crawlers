"""Modules responsible for data crawling."""
import datetime
import re
from core.navigation import UrlBuilder
from core.navigation import Browser


def get_element_text(element):
    """Build the element text by iterating through child elements.

    Parameters
    ----------
    element: lxml.Element
        The element for which to build text.

    Returns
    -------
    text: str
        The inner text of the element.
    """
    parts = [text.strip() for text in element.itertext()]
    text = ''.join([p for p in parts if len(p) > 0])
    return text.strip()


class SessionUrlsCrawler:
    """Crawl session URLs for a specific year."""

    SessionUrlRegex = r"\/pls\/steno\/steno2015.data\?cam=2&dat=(?P<date>\d{8})&idl=1"

    def __init__(self):
        """Create a new instance of session URLs crawler."""
        self.__url_builder = UrlBuilder()
        self.__browser = Browser()

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
        html_root = self.__browser.load_page(url)
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
