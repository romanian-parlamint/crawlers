"""Modules required for navigation."""
import logging
from lxml import html
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options


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


class Browser:
    """Load page markup from the URLs."""

    def __init__(self):
        """Create a new instance of the class."""
        self.__browser_options = Options()
        self.__browser_options.add_argument('-headless')

    def load_page(self, url):
        """Request the page for the specified URL and returns the HTML markup.

        Parameters
        ----------
        url: str, required
            The URL of the page to load.

        Returns
        -------
        html: etree.Element
            The HTML of the page parsed into a tree structure.
        """
        logging.info("Navigating to {}.".format(url))
        browser = Firefox(options=self.__browser_options)
        browser.get(url)
        page_source = browser.page_source
        browser.quit()
        return html.fromstring(page_source)
