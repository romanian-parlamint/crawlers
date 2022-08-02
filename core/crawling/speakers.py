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
        fonts = [f for f in element.iterdescendants(tag='font')]
        if len(fonts) == 0:
            # The element doesn't contain the name of a speaker
            return None

        text = element.text_content().strip()

        # Parse full name of the speaker
        name_element_text = fonts[0].text_content()
        sex = 'M' if name_element_text.startswith("Domnul") else 'F'
        full_name = re.sub(r'domnul|doamna|(\(.+\)*)?:', '', name_element_text,
                           0, re.MULTILINE | re.IGNORECASE)
        full_name = full_name.strip()

        # Get profile URL if present
        profile_url = None
        anchors = [
            a for a in element.iterdescendants(tag='a')
            if a.get('target') == "PARLAMENTARI"
        ]
        if len(anchors) > 0:
            profile_url = anchors[0].get('href')
            profile_url = self.__ulr_builder.build_full_URL(profile_url)

        # Get annotation if present
        annotation = None
        comments = [i for i in element.iterdescendants(tag='i')]
        if len(comments) > 0:
            annotation = comments[0].text_content()

        return {
            'text': text,
            'full_name': full_name,
            'profile_url': profile_url,
            'sex': sex,
            'annotation': annotation
        }
