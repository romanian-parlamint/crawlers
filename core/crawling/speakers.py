"""Module responsible for crawling speaker info."""
from core.navigation import UrlBuilder
from core.navigation import Browser
import re


class SpeakerInfoParser:
    """Parse the speaker information."""

    def __init__(self):
        """Create a new instance of the class."""
        self.__ulr_builder = UrlBuilder()

    def parse(self, element):
        """Parse speaker info from the provided element.

        Parameters
        ----------
        element: etree.Element, required
            The element to parse.

        Returns
        -------
        speaker: dict
            The parsed speaker information.
        """
        name_element = self.__get_name_element(element)
        if name_element is None:
            return None

        name_with_prefix = name_element.text_content()

        speaker = {
            'text': element.text_content().strip(),
            'full_name': self.__parse_full_name(name_with_prefix),
            'profile_url': self.__parse_profile_url(element),
            'sex': self.__parse_speaker_sex(name_with_prefix),
            'annotation': self.__parse_annotation(element)
        }

        return speaker

    def __get_name_element(self, element):
        """Get the name element from the provided element, if present.

        Parameters
        ----------
        element: etree.Element, required
            The parent element from which to extract name element.

        Returns
        -------
        name_element: etree.Element
            The name element if present; None otherwise.
        """
        fonts = [f for f in element.iterdescendants(tag='font')]
        if len(fonts) == 0:
            # The element doesn't contain the name of a speaker
            return None

        return fonts[0]

    def __parse_speaker_sex(self, name_with_prefix):
        """Parse speaker sex from the text containing name and prefix.

        Parameters
        ----------
        name_with_prefix: str, required
            The name and prefix of the speaker.

        Returns
        -------
        sex: str
            The sex of the speaker; 'M' if male, 'F' if female.
        """
        return 'M' if name_with_prefix.lower().startswith("domnul") else 'F'

    def __parse_full_name(self, name_with_prefix):
        """Parse the full name of the speaker from the name with prefix.

        Parameters
        ----------
        name_with_prefix: str, required
            The name and prefix of the speaker.

        Returns
        -------
        full_name: str
            The full name of the speaker.
        """
        full_name = re.sub(r'domnul|doamna|(\(.+\)*)?:', '', name_with_prefix,
                           0, re.MULTILINE | re.IGNORECASE)
        return full_name.strip()

    def __parse_profile_url(self, element):
        """Parse the profile URL of the speaker if present.

        Parameters
        ----------
        element: etree.Element, required
             The element containing speaker information.

        Returns
        -------
        profile_url: str
            The full URL of the speaker profile if present; otherwise None.
        """
        profile_url = None
        anchors = [
            a for a in element.iterdescendants(tag='a')
            if a.get('target') == "PARLAMENTARI"
        ]

        if len(anchors) > 0:
            profile_url = anchors[0].get('href')
            profile_url = self.__ulr_builder.build_full_URL(profile_url)

        return profile_url

    def __parse_annotation(self, element):
        """Parse the annotation from speaker info element if present.

        Parameters
        ----------
        element: etree.Element, required
             The element containing speaker information.

        Returns
        -------
        annotation: str
            The annotation beside the speaker name if present; otherwise None.
        """
        annotation = None
        comments = [i for i in element.iterdescendants(tag='i')]
        if len(comments) > 0:
            annotation = comments[0].text_content()
        return annotation


class SpeakerProfileCrawler:
    """Crawl speaker profile page."""

    def __init__(self):
        """Create a new instance of the class."""
        self.__browser = Browser()

    def crawl(self, profile_url):
        """Crawl speaker profile data from provided URL.

        Parameters
        ----------
        profile_url: str, required
            The profile URL of the speaker.

        Returns
        -------
        profile_info: dict
            The information parsed from the profile page.
        """
        html_root = self.__browser.load_page(profile_url)
        first_name, last_name = self.__parse_name(html_root)
        profile_info = {
            'first_name': first_name,
            'last_name': last_name,
            'mp_type': self.__parse_mp_type(html_root),
            'affiliation': None,
            'profile_picture': None
        }
        return profile_info

    def __parse_name(self, html_root):
        """Parse the first and last names from the provided element.

        Parameters
        ----------
        html_root: etree.Element, required
            The HTML root of the profile page.

        Returns
        -------
        (first_name, last_name): tuple of (list of str, list of str)
            The first and last names of the speaker split into constituent parts by space.
        """
        name_elements = list(html_root.cssselect('div.boxTitle h1'))
        if len(name_elements) == 0:
            return (None, None)
        name = name_elements[0].text_content()
        first_name, last_name = [], []
        for part in name.split():
            if part.isupper():
                last_name.append(part)
            else:
                first_name.append(part)
        return first_name, last_name

    def __parse_mp_type(self, html_root):
        """Parse the type of member of parliament from profile page.

        Parameters
        ----------
        html_root: etree.Element, required
            The HTML root of the profile page.

        Returns
        -------
        mp_type: str
            The type of member of parliament; can be either 'Senator' or 'Deputy'.
        """
        profile_sections = list(html_root.cssselect('div.boxDep h3'))
        member_type = profile_sections[0]
        member_type_text = member_type.text_content()
        if 'deputat' in member_type_text.lower():
            return 'Deputy'
        else:
            return 'Senator'
