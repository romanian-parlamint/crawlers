"""Module responsible for parsing MP profile info from page."""
from lxml.etree import Element


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
        return {'profile_image': profile_image_url}

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
