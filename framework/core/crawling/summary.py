"""Module responsible for crawling session summary."""
import logging
from urllib.parse import urlparse as parse_url
from urllib.parse import parse_qs
from framework.core.navigation import UrlBuilder
from framework.core.navigation import Browser


class SessionSummaryCrawler:
    """Crawl session summary from the summary page."""

    SessionSummaryUrlPath = "/pls/steno/steno2015.sumar?"

    def __init__(self):
        """Create a new instance of session summary crawler."""
        self.__url_builder = UrlBuilder()
        self.__browser = Browser()
        self.__summary_parser = SessionSummaryParser()
        self.__summary_urls_parser = SummaryUrlsParser()

    def crawl(self, session_url):
        """Crawl the summary of the session.

        Parameters
        ----------
        session_url: str, required
            The URL of the session.

        Returns
        -------
        summaries: list of dict
            The summaries of the sessions from the URL
        """
        html_root = self.__browser.load_page(session_url)
        if self.__is_single_session_summary(html_root):
            logging.info(
                "The URL {} contains the summary of a single session.".format(
                    session_url))
            return [self.__summary_parser.parse(html_root)]
        else:
            logging.info(
                "The URL {} contains the summary of multiple sessions.".format(
                    session_url))
            summaries = []
            for summary_url in self.__summary_urls_parser.parse(html_root):
                html_root = self.__browser.load_page(summary_url)
                summaries.append(self.__summary_parser.parse(html_root))
        return summaries

    def __is_single_session_summary(self, html_root):
        """Determine whether the provided HTML tree contains the summary of a single session or multiple sessions.

        Parameters
        ----------
        html_root: etree.Element, required
            The HTML tree.

        Returns
        -------
        is_single_session_summary: bool
            True if the HTML contains the summary of a single session; False otherwise.
        """
        return len(self.__summary_urls_parser.parse(html_root)) == 1


class SummaryUrlsParser:
    """Parse the summary URLs from page."""

    def __init__(self):
        """Create a new instance of the class."""
        self.__url_builder = UrlBuilder()

    def parse(self, html_root):
        """Parse the summary URLs when there are multiple summaries on the page.

        Parameters
        ----------
        html_root: etree.Element, required
            The HTML tree.

        Returns
        -------
        urls: list of str,
            The URLs of session summaries.
        """
        summary_urls = set()
        for title_box in html_root.cssselect("div.boxTitle"):
            full_url = self.__get_full_url(title_box.getparent())
            if full_url is None:
                continue

            summary_urls.add(full_url)

        for anchor in html_root.cssselect("div.resurse-list a[href*='sumar']"):
            summary_urls.add(self.__get_full_url(anchor))
        return list(summary_urls)

    def __get_full_url(self, anchor):
        """Get the full URL from the 'href' property of the given anchor element.

        Parameters
        ----------
        anchor: etree.Element, required
            The anchor from which to extract the URL.

        Returns
        -------
        full_url: str
            The URL retrieved from anchor prepended with domain name and protocol.
        """
        path_and_query = anchor.get('href')
        if path_and_query is None:
            logging.error(
                "Could not find the link for session summary for {}.".format(
                    anchor.text_content()))
            return None
        full_url = self.__url_builder.build_full_URL(path_and_query)
        return full_url


class SessionSummaryParser:
    """Parse the session summary."""

    def __init__(self):
        """Create a new instance of the class."""
        self.__url_builder = UrlBuilder()
        self.__summary_urls_parser = SummaryUrlsParser()

    def parse(self, html_root):
        """Parse the summary of a single session.

        Parameters
        ----------
        html_root: etree.Element, required
            The HTML tree.

        Returns
        -------
        summary: dict
            The summary of the session.
        """
        summary_rows = self.__parse_summary_rows(html_root)
        transcript_url = self.__parse_full_transcript_url(html_root)
        return {
            'session_id': self.__parse_session_id(html_root),
            'session_title': self.__parse_session_title(html_root),
            'full_transcript_url': transcript_url,
            'summary': summary_rows
        }

    def __parse_session_title(self, html_root):
        """Parse session title from HTML markup.

        Parameters
        ----------
        html_root: etree.Element, required
            The HTML tree.

        Returns
        -------
        title: str
            The title of the session if found; otherwise None.
        """
        headings = [
            title for title in html_root.xpath("//div[@class='box-title']/h3")
        ]
        session_title = headings[-1]
        return session_title.text_content()

    def __parse_summary_rows(self, html_root):
        """Parse summary rows from page.

        Parameters
        ----------
        html_root: etree.Element, required
            The HTML tree.

        Returns
        -------
        summary_rows: iterable of dict
            The summary rows of the session.
        """
        summary_table = html_root.xpath("//div[@id='olddiv']/table")[0]
        summary_rows = []
        for tr in summary_table.iterdescendants(tag="tr"):
            number, url, contents, is_subrow = self.__parse_summary_row(tr)
            if is_subrow:
                last_row = summary_rows[-1]
                last_row['contents'].extend(contents)
            else:
                row = {
                    'number': number,
                    'url': self.__url_builder.build_full_URL(url),
                    'contents': contents
                }
                summary_rows.append(row)
        return summary_rows

    def __parse_summary_row(self, tr):
        """Parse summary row from page.

        Parameters
        ----------
        tr: etree.Element, required
            The row of the summary table to parse.

        Returns
        -------
        (number, url, contents, is_subrow): tuple of (str, str, list of str, bool
            A tuple containing the row number, the relative URL to the text of the discussion,
            a list of the contents, and an indicator whether the current row is a subrow
            or a normal row.
        """
        anchors = [a for a in tr.iterdescendants(tag='a')]
        number, url = None, None
        if len(anchors) > 0:
            a = anchors[0]
            number = a.text_content()
            url = a.get('href')

        row_parser = SummaryRowContentsParser(tr)
        contents = row_parser.parse()
        is_subrow = row_parser.is_subrow

        return (number, url, contents, is_subrow)

    def __parse_full_transcript_url(self, html_root):
        """Parse the URL of the full session transcript.

        Parameters
        ----------
        html_root: etree.Element, required
            The HTML tree.

        Returns
        -------
        url: str
            The URL of the full session transcript.
        """
        # Take the last div with the class 'resurse-list'
        resources_div = html_root.xpath("//div[@class='resurse-list']")[-1]
        # From the div return the href of the second anchor
        links = [a for a in resources_div.iterdescendants(tag="a")]
        path_and_query = links[1].get('href')
        return self.__url_builder.build_full_URL(path_and_query)

    def __parse_session_id(self, html_root):
        """Parse the id of the session from summary page.

        Parameters
        ----------
        html_root: etree.Element, required
            The HTML tree.

        Returns
        -------
        session_id: str
            The id of the session.
        """
        urls = self.__summary_urls_parser.parse(html_root)
        for url in urls:
            query_string = parse_qs(parse_url(url).query)
            if 'ids' in query_string:
                return query_string['ids'][0]

        logging.error("Could not parse session id from URLS [{}]".format(
            ', '.join(list(urls))))
        return None


class SummaryRowContentsParser:
    """Parse the contents of a session summary row."""

    def __init__(self, row):
        """Create a new instance of the class.

        Parameters
        ----------
        row: etree.Element, required
            The summary row to parse.
        """
        columns = [td for td in row.iterdescendants(tag='td')]
        # If the number of columns is 3 then the current row is a subrow.
        # In such case, we take the whole text of the row as the contents;
        # otherwise, the contents are taken from the second column of the row.
        self.__is_subrow = len(columns) == 3
        self.__contents_source = row if self.__is_subrow else columns[1]

    @property
    def is_subrow(self):
        """Get a flag indicating whether the current row is a subrow or now.

        Returns
        -------
        is_subrow: bool
            True if curent row is a subrow, False otherwise.
        """
        return self.__is_subrow

    @property
    def has_multiple_lines(self):
        """Get a flag indicating if content of current row has multiple lines.

        Returns
        -------
        has_multiple_lines: bool
            True if current row has multi-line content; False otherwise.
        """
        if self.is_subrow:
            return False
        return self.__contents_source.find('br') is not None

    @property
    def annotation_element(self):
        """Get the annotation element if present.

        Returns
        -------
        annotation_element: etree.Element
            The annotation element if present; otherwise None.
        """
        return self.__contents_source.find('i')

    @property
    def has_annotation(self):
        """Get a flag indicating if the content of current row has an annotation.

        Returns
        -------
        has_annotation: bool,
            True if current row has annotation; False otherwise.
        """
        if self.is_subrow:
            return False
        return self.annotation_element is not None

    def parse(self):
        """Parse the contents of the summary row.

        Returns
        -------
        contents: list of dict
            A list of dicts with two keys: 'contents', and 'annotation'.
        """
        if self.is_subrow:
            return [{
                'line_contents': self.__parse_subrow_contents(),
                'annotation': None
            }]

        if self.has_annotation:
            (contents, annotation) = self.__parse_content_with_annotation()
            return [{'line_contents': contents, 'annotation': annotation}]

        if self.has_multiple_lines:
            return [{
                'line_contents': c,
                'annotation': None
            } for c in self.__parse_multi_line_contents()]

        return [{'line_contents': self.__parse_contents(), 'annotation': None}]

    def __parse_subrow_contents(self):
        """Parse the contents of a subrow.

        Returns
        -------
        contents: str
            The contents of the subrow.
        """
        contents = []
        for raw_text in self.__contents_source.itertext():
            text = raw_text.strip()
            if text is not None and len(text) > 0:
                contents.append(text)
        return [' '.join(contents)]

    def __parse_content_with_annotation(self):
        """Parse the contents of a row with an annotation.

        Returns
        -------
        (contents, annotation): tuple of (str, str)
            The contents and annotation of the row.
        """
        contents = "".join(
            [t.strip() for t in self.__contents_source.itertext()])
        annotation = self.annotation_element.text
        return (contents, annotation)

    def __parse_multi_line_contents(self):
        """Parse the contents of a row with multiple lines.

        Returns
        -------
        content_lines: list of str
            The content lines of the row.
        """
        content_lines = [
            t.strip() for t in self.__contents_source.itertext()
            if len(t.strip()) > 0
        ]
        return content_lines

    def __parse_contents(self):
        """Parse the contents of a summary row.

        Returns
        -------
        contents: str
            The contents of the row.
        """
        return self.__contents_source.text.strip()
