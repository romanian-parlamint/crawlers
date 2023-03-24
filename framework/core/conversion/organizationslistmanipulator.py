"""Class for manipulating the list of organizations."""
from .xmlutils import XmlElements, XmlAttributes
from datetime import date
from lxml import etree
from typing import Generator
from typing import List
from typing import Tuple
import logging
from .namedtuples import Event


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
        self.__government_org = None
        self.__executive_terms = None

    @property
    def parliament(self) -> etree.Element:
        """Get the parliament organization.

        Returns
        -------
        parliament: etree.Element,
            The organization with role==parliament.
        """ ""
        if self.__parliament_org is None:
            self.__parliament_org = self.__get_organization_with_role(
                "parliament")
        return self.__parliament_org

    @property
    def government(self) -> etree.Element:
        """Get the government organization.

        Returns
        -------
        parliament: etree.Element,
            The organization with role==parliament.
        """ ""
        if self.__government_org is None:
            self.__government_org = self.__get_organization_with_role(
                "government")
        return self.__government_org

    @property
    def legislative_terms(self) -> List[Tuple[str, str, date, date]]:
        """Get the legislative terms of the Parliament from the corpus root file.

        Returns
        -------
        legislative_terms: list of (str, str, date, date) tuples
            The legislative terms as tuples of (id, organization id, start date, end date).
        """
        if self.__legislative_terms is None:
            terms = list(self.__load_organization_events(self.parliament))
            self.__legislative_terms = terms
        return self.__legislative_terms

    @property
    def executive_terms(self) -> List[Tuple[str, str, date, date]]:
        """Get the executive terms of the Government from the corpus root file.

        Returns
        -------
        terms: list of (str, str, date, date) tuples
            The executive terms as tuples of (id, organization id, start date, end date).
        """
        if self.__executive_terms is None:
            terms = list(self.__load_organization_events(self.government))
            self.__executive_terms = terms
        return self.__executive_terms

    def get_legislative_term(self, session_date: date) -> Event:
        """Get the legislative term for the specified session date.

        Parameters
        ----------
        session_date: date, required
            The date of the session.

        Returns
        -------
        event: Event
            The event for the specified date if found; otherwise an Event with all properties set to None.
        """
        return self.__find_event_for_date(self.legislative_terms, session_date)

    def get_executive_term(self, session_date: date) -> Event:
        """Get the executive term for the specified session date.

        Parameters
        ----------
        session_date: date, required
            The date of the session.

        Returns
        -------
        event: Event
            The event for the specified date if found; otherwise an Event with all properties set to None.
        """
        return self.__find_event_for_date(self.executive_terms, session_date)

    def __find_event_for_date(self, events: List[Event],
                              session_date: date) -> Event:
        """Find the event for provided date.

        Parameters
        ----------
        events: list of Event, required
            The list where to search for the event.
        session_date: date, required
            The date of the session.

        Returns
        -------
        event: Event
            The event for the specified date if found; otherwise an event with None for all properties.
        """
        for event in events:
            _, _, start_date, end = event
            end_date = date.max if end is None else end
            if start_date <= session_date <= end_date:
                return event
        logging.error("Could not find event for session date %s.",
                      session_date)
        return Event(None, None, None, None)

    def __load_organization_events(
            self, organization: etree.Element) -> Generator[Event, None, None]:
        """Load the events of the provided organization.

        Parameters
        ----------
        organization: etree.Element
            The organization for which to load the events.

        Returns
        -------
        events: generator of Term
            The list of events.
        """
        org_id = "#{}".format(organization.get(XmlAttributes.xml_id))
        for event in organization.iterdescendants(tag=XmlElements.event):
            event_id = "#{}".format(event.get(XmlAttributes.xml_id))
            start_date = date.fromisoformat(
                event.get(XmlAttributes.event_start))
            event_end = event.get(XmlAttributes.event_end)
            end_date = date.fromisoformat(
                event_end) if event_end is not None else None
            yield Event(org_id, event_id, start_date, end_date)

    def __get_organization_with_role(self, role: str) -> etree.Element:
        """Get the first organization with the specified role.

        Parameters
        ----------
        role: str, required
            The role of the organization.

        Returns
        -------
        organization: etree.Element
            The organization with the specified role; None if not found.
        """
        for org in self.__xml_root.iterdescendants(tag=XmlElements.org):
            if org.get(XmlAttributes.role) == role:
                return org
        return None
