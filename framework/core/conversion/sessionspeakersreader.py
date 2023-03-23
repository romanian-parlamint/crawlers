"""Class for reading session speakers."""
from .xmlutils import XmlDataManipulator
from .xmlutils import XmlElements, XmlAttributes
from datetime import datetime
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
        speaker_ids:  list of str
            The list of unique speaker ids.
        """
        ids = set()
        for utterance in self.xml_root.iterdescendants(tag=XmlElements.u):
            speaker_id = utterance.get(XmlAttributes.who)
            ids.add(speaker_id)
        return list(ids)
