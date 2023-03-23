"""Class for manipulating the list of organizations."""
from .xmlutils import XmlElements, XmlAttributes
from datetime import date
from lxml import etree
from typing import Generator
from typing import List
from typing import Tuple
import logging


class OrganizationsListManipulator:
    """Handles queries on the `listOrg` element contents."""

    def __init__(self, xml_root: etree.Element):
        """Create a new instance of the class.

        Parameters
        ----------
        xml_root: etree.Element, required
            The root node of the corpus root file.
        """
        self.__xml_root = xml_root
        self.__parliament_org = None
        self.__legislative_terms = None

    @property
    def parliament(self) -> etree.Element:
        """Get the parliament organization.

        Returns
        -------
        parliament: etree.Element,
            The organization with role==parliament.
        """ ""
        if self.__parliament_org is None:
            for org in self.__xml_root.iterdescendants(tag=XmlElements.org):
                if org.get(XmlAttributes.role) == "parliament":
                    self.__parliament_org = org
        return self.__parliament_org

    @property
    def legislative_terms(self) -> List[Tuple[str, str, date, date]]:
        """Get the legislative terms of the Parliament from the corpus root file.

        Returns
        -------
        legislative_terms: list of (str, str, date, date) tuples
            The legislative terms as tuples of (id, organization id, start date, end date).
        """
        if self.__legislative_terms is None:
            self.__legislative_terms = list(self.__load_legislative_terms())
        return self.__legislative_terms

    def get_legislative_term(
            self, session_date: date) -> Tuple[str, str, date, date]:
        """Get the legislative term for the specified session date.

        Returns
        -------
        (term_id, org_id, start_date, end_date): tuple of (str, date, date)
            The tuple containing the term id, organization id, start date and end date
            of the legislative term if found; otherwise (None, None, None, None).
        """
        for term in self.legislative_terms:
            _, _, term_start, term_end = term
            end_date = date.max if term_end is None else term_end
            if term_start <= session_date <= end_date:
                return term

        logging.error("Could not find legislative term for session date %s.",
                      session_date)
        return (None, None, None, None)

    def __load_legislative_terms(
            self) -> Generator[Tuple[str, str, date, date], None, None]:
        """Load legislative terms from the root file.

        Returns
        legislative_terms: generator of (str, str, date, date) tuples
            The list of legislative terms as tuples of (term id, parliament organization id, start date, end date).
        """
        parliament = self.parliament
        org_id = "#{}".format(parliament.get(XmlAttributes.xml_id))
        for event in parliament.iterdescendants(tag=XmlElements.event):
            term_id = "#{}".format(event.get(XmlAttributes.xml_id))
            term_start = date.fromisoformat(
                event.get(XmlAttributes.event_start))
            event_end = event.get(XmlAttributes.event_end)
            term_end = date.fromisoformat(
                event_end) if event_end is not None else None
            yield (term_id, org_id, term_start, term_end)
