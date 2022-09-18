"""Module responsible for crawling MP profile."""
from framework.core.navigation import Browser
from framework.core.navigation import UrlBuilder
from framework.core.parsing.memberprofile import MemberProfileInfoParser


class MemberProfileCrawler:
    """Crawl the profile info for Members of Parliament."""

    def __init__(self):
        """Create a new instance of the MP profile crawler class."""
        self.__browser = Browser()
        self.__parser = MemberProfileInfoParser()
        self.__url_builder = UrlBuilder()

    def crawl(self, profile_url: str) -> dict:
        """Crawl the MP profile info.

        Parameters
        ----------
        profile_url: str, required
            The URL of the MP profile.

        Returns
        -------
        profile_info: dict
            The dict containing profile info.
        """
        html = self.__browser.load_page(profile_url)
        profile_info = self.__parser.parse_profile_info(html)
        profile_image = profile_info['profile_image']
        if profile_image is not None:
            profile_info['profile_image'] = self.__url_builder.build_full_URL(
                profile_image)
        return profile_info
