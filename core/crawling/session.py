"""Module responsible for crawling session transcript."""
import logging
import re
import datetime
from core.navigation import UrlBuilder
from core.navigation import Browser
from core.crawling.utils import get_element_text


class SessionTranscriptCrawler:
    """Crawl session transcript."""

    def __init__(self):
        """Create a new instance of session transcript crawler."""
        self.__url_builder = UrlBuilder()
        self.__browser = Browser()

    def crawl(self, session_date, session_url):
        """Crawl the transcript of the session.

        Parameters
        ----------
        session_date: datetime.date, required
            The date of the session.
        session_url: str, required
            The URL of the session.

        Returns
        -------
        transcript: dict
            The session transcript.
        """
        transcript_table = self.__get_transcript_table(session_url)
        if transcript_table is None:
            return {}
        contents = self.__get_transcript_contents(transcript_table)
        start_end_parser = SessionStartEndParser(session_date)
        transcript = {
            'start': start_end_parser.parse_start_section(contents[0]),
            'end': start_end_parser.parse_end_section(contents[-1])
        }
        return transcript

    def __get_transcript_contents(self, transcript_table):
        """Build a list of 'td' elements that contain the transcript.

        Parameters
        ----------
        transcript_table: etree.Element, required
            The table containing session transcript.

        Returns
        -------
        contents: list of etree.Element
            The contents of session transcript.
        """
        contents = []
        for td in transcript_table.iterdescendants(tag='td'):
            width = td.get('width')
            if width is not None and "100" in width:
                contents.append(td)
        return contents

    def __get_transcript_table(self, session_url):
        """Load the transcript page and returns the table containing session segments.

        Parameters
        ----------
        session_url: str, required
            The URL of the session.

        Returns
        -------
        transcript_table: etree.Element
            The table element containing session segments.
        """
        html_root = self.__browser.load_page(session_url)
        tables = html_root.xpath("//div[@id='olddiv']/table")
        if len(tables) == 0:
            logging.error(
                "Could not locate transcript table for URL {}.".format(
                    session_url))
            return None
        return tables[0]


class SessionStartEndParser:
    """Parse the start and end sections of a session transcript."""

    def __init__(self, session_date):
        """Create a new instance of the class.

        Parameters
        ----------
        session_date: datetime.date, required
            The date of the session.
        """
        self.__session_date = session_date

    @property
    def session_date(self):
        """Get session date as an ISO formatted string."""
        return self.__session_date.strftime("%Y-%m-%d")

    def parse_start_section(self, element):
        """Parse the contents of the start section.

        Parameters
        ----------
        element: etree.Element, required
            The element containing the start section.

        Returns
        -------
        section: dict,
            The contents of start section.
        """
        para = [p for p in element.iterdescendants(tag='p')]
        if len(para) == 0:
            logging.error(
                "Cannot parse session start info for session from {}.".format(
                    self.session_date))
            return {}

        start_mark = get_element_text(para[0])
        start_time = self.__parse_time(start_mark)
        session_chairmen = self.__parse_chairmen(
            para[1] if len(para) > 1 else None)
        return {
            'start_mark': start_mark,
            'start_time': start_time,
            'chairmen': session_chairmen
        }

    def parse_end_section(self, element):
        """Parse the contents of the end section.

        Parameters
        ----------
        element: etree.Element, required
            The element containing the end section.

        Returns
        section: dict,
            The contents of the end section if parsing succeeds; None otherwise.
        """
        if element is None:
            logging.error(
                "Cannot parse end segment of session from {}.".format(
                    self.session_date))
            return None
        # Get the last <p> element from the node given as parameter
        end_section = [p for p in element.iterdescendants(tag='p')][-1]
        end_mark = get_element_text(end_section)
        end_time = self.__parse_time(end_mark)
        return {'end_mark': end_mark, 'end_time': end_time}

    def __parse_time(self, line):
        """Parse the time from the specified text line.

        Parameters
        ----------
        line: str, required
            The text line containing the time to parse.

        Returns
        -------
        time: datetime
            The date and time when session started; None if parsing failed.
        """
        # Some session transcripts use period as hour and time separator,
        # others use comma. The regex below tries to match any of them in an
        # unnamed group. The digits on the left are captured as hour and
        # time into two separate capturing groups.
        pattern = r"(?P<hour>\d{1,2})(\.|,)(?P<minute>\d{2})\.$"
        match = re.search(pattern, line, re.MULTILINE)
        if not match:
            logging.error(
                "Could not parse time from line '{}' for session date {}.".
                format(line, self.session_date))
            return None
        hour = int(match.group('hour'))
        minute = int(match.group('minute'))
        session_time = datetime.datetime.combine(
            self.__session_date, datetime.time(hour=hour, minute=minute))
        return session_time.isoformat()

    def __parse_chairmen(self, element):
        """Parse the info about who is presiding the session.

        Parameters
        ----------
        element: etree.Element, required
            The element containing info about the session chairmen.

        Returns
        -------
        chairmen: str
            The string containing the chairmen info; None if parsing failed.
        """
        if element is None:
            logging.error(
                "Could not parse session chairmen for session on {}.".format(
                    self.session_date))
            return None
        return get_element_text(element)
