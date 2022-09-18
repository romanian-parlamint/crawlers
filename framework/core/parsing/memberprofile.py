"""Module responsible for parsing MP profile info from page."""
from lxml.etree import Element
from typing import Tuple, Iterable


class MemberProfileInfoParser:
    """Parse the profile info of Members of Parliament."""

    def parse_profile_info(self, html: Element) -> dict:
        """Parse the profile info from the provided HTML element.

        Parameters
        ----------
        html: etree.Element, required
            The root HTML element of the page containing profile info.

        Returns
        -------
        profile_info: dict
            The profile data of the MP.
        """
        profile_image_url = self.__parse_profile_image(html)
        full_name = self.__parse_full_name(html)
        first_name, last_name = self.__get_name_parts(full_name)
        return {
            'profile_image': profile_image_url,
            'full_name': full_name,
            'first_name': first_name,
            'last_name': last_name
        }

    def __parse_profile_image(self, html: Element) -> str:
        """Parse the URL of the profile image from the provided HTML.

        Parameters
        ----------
        html: etree.Element, required
            The root HTML element of the page containing profile info.

        Returns
        -------
        image_url: str
            The URL of the profile image if found; None otherwise.
        """
        for a in html.cssselect('div.profile-pic-dep a'):
            return a.get('href')

        return None

    def __parse_full_name(self, html: Element) -> str:
        """Parse full name of the MP from profile page.

        Parameters
        ----------
        html: etree.Element, required
            The root HTML element of the page containing profile info.

        Returns
        -------
        full_name: str
            The full name of the MP.
        """
        for h1 in html.cssselect('div.boxTitle h1'):
            return h1.text_content()

        return None

    def __get_name_parts(
            self, full_name: str) -> Tuple[Iterable[str], Iterable[str]]:
        """Split the full name into first and last names.

        Parameters
        ----------
        full_name: str, required
            The full name of the MP as it appears on his/her profile.

        Returns
        -------
        (first_name, last_name): tuple of iterable of strings
            The name parts.
        """
        first_name, last_name = [], []
        for part in full_name.strip().split():
            if part.isupper():
                last_name.append(part)
            else:
                first_name.append(part)
        return first_name, last_name
