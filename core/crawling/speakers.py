"""Module responsible for crawling speaker info."""
from core.navigation import UrlBuilder
from core.navigation import Browser
import re


class SpeakerInfoParser:
    """Parse the speaker information."""

    def __init__(self):
        """Create a new instance of the class."""
        self.__ulr_builder = UrlBuilder()
        self.__browser = Browser()

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

        return {
            'text': element.text_content().strip(),
            'full_name': self.__parse_full_name(name_with_prefix),
            'profile_url': self.__parse_profile_url(element),
            'sex': self.__parse_speaker_sex(name_with_prefix),
            'annotation': self.__parse_annotation(element)
        }

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
