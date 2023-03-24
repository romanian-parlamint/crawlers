"""Class for reading session speakers."""
from .xmlutils import XmlDataManipulator
from .xmlutils import XmlElements, XmlAttributes
from datetime import datetime
from lxml import etree
from typing import List


class SessionSpeakersReader(XmlDataManipulator):
    """Read session speakers."""

    def __init__(self, file_path: str):
        """Create a new instance of the class.

        Parameters
        ----------
        file_path: str, required
            The path of the XML file containing session transcript.
        """
        XmlDataManipulator.__init__(self, file_path)
        self.__session_date = None

    @property
    def session_date(self):
        """Get the session date."""
        if self.__session_date is None:
            for date_elem in self.xml_root.iterdescendants(
                    tag=XmlElements.date):
                if date_elem.getparent().tag != XmlElements.bibl:
                    continue
                date = datetime.fromisoformat(date_elem.get(
                    XmlAttributes.when))
                self.__session_date = date.date()

        return self.__session_date

    def get_speaker_ids(self) -> List[str]:
        """Read speaked ids from the session transcript.

        Returns
        -------
        (speaker_ids, gov_members):  tuple of list of str
            The list of unique speaker ids, and the list of unique government members.
        """
        ids, gov_members = set(), set()
        for utterance in self.xml_root.iterdescendants(tag=XmlElements.u):
            speaker_id = utterance.get(XmlAttributes.who)
            ids.add(speaker_id)
            if self.__is_of_a_government_member(utterance):
                gov_members.add(speaker_id)
        return list(ids), list(gov_members)

    def __is_of_a_government_member(self, utterance: etree.Element) -> bool:
        """Check if the utterance is of a government member.

        Parameters
        ----------
        utterance: etree.Element, required
            The utterance to check.

        Returns
        -------
        is_goverment_member: bool
            True if the speaker is a government member; false otherwise.
        """
        note = utterance.getprevious()
        if note is None:
            return False
        if note.tag != XmlElements.note:
            return False
        return 'ministru' in note.text.lower()
