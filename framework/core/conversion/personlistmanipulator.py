"""Class for manipulating person elements."""
from lxml import etree
from .xmlutils import XmlElements, XmlAttributes
from .namedtuples import Event, PersonalInformation
from typing import List


class PersonListManipulator:
    """Hadles updates and queries on the `listPerson` element contents."""

    def __init__(self, xml_root: etree.Element):
        """Create a new instance of the class.

        Parameters
        ----------
        xml_root: etree.Element, required
            The root node of the corpus root file.
        """
        self.__xml_root = xml_root
        self.__persons_list = next(
            xml_root.iterdescendants(tag=XmlElements.listPerson))

    def add_or_update_person(self, person_id: str, legislative_term: Event,
                             personal_info: PersonalInformation):
        """Add or update person.

        Parameters
        ----------
        person_id: str, required
            The id of the person to add or update.
        legislative_term: tuple of (str, str, date, date), required
            The legislative term as a tuple of (term id, organization id, start date, end date) in which the person appears.
        personal_info: PersonalInformation, required
            The personal information.
        """
        person_id = person_id.replace('#', '')
        person = self.__get_person(person_id)
        if person is None:
            person = self.__create_person(person_id, personal_info.first_name,
                                          personal_info.last_name,
                                          personal_info.sex,
                                          personal_info.profile_image)
        self.__update_affiliation(person, legislative_term)

    def __update_affiliation(self, person: etree.Element,
                             legislative_term: Event):
        """Add the legislative term to the affiliation of the person if it doesn't exist.

        Parameters
        ----------
        person: etree.Element, required
            The person element to update.
        legislative_term: tuple of (str, str, date, date), required
            The id, organization id, start date, and end date of the legislative term.
        """
        organization_id, term_id, start_date, end_date = legislative_term
        for affiliation in person.iterdescendants(tag=XmlElements.affiliation):
            if affiliation.get(XmlAttributes.ana) == term_id:
                # Affiliation already exists; nothing to do.
                return

        affiliation = etree.SubElement(person, XmlElements.affiliation)
        affiliation.set(XmlAttributes.ana, term_id)
        affiliation.set(XmlAttributes.ref, organization_id)
        affiliation.set(XmlAttributes.role, "member")
        affiliation.set(XmlAttributes.event_start,
                        start_date.strftime("%Y-%m-%d"))
        if end_date is not None:
            affiliation.set(XmlAttributes.event_end,
                            end_date.strftime("%Y-%m-%d"))

    def __create_person(self,
                        person_id: str,
                        first_name: List[str],
                        last_name: List[str],
                        sex: str = None,
                        profile_image: str = None) -> etree.Element:
        """Create a person element with the provided info.

        Parameters
        ----------
        person_id: str, required
            The id of the person element.
        first_name: list of str, required
            The first name of the person.
        last_name: list of str, required
            The last name of the person.
        sex: str, optional
            The sex of the person.
        profile_image: str, optional
            The URL of the profile image of the person.

        Returns
        -------
        person: etree.Element
            The person element.
        """
        person = etree.SubElement(self.__persons_list, XmlElements.person)
        person.set(XmlAttributes.xml_id, person_id)

        person_name = etree.SubElement(person, XmlElements.persName)
        for part in first_name:
            forename = etree.SubElement(person_name, XmlElements.forename)
            forename.text = part

        for part in last_name:
            surname = etree.SubElement(person_name, XmlElements.surname)
            surname.text = part

        sex_element = etree.SubElement(person, XmlElements.sex)
        sex = sex if sex is not None else 'U'
        sex_element.set(XmlAttributes.value, sex)

        if profile_image is not None:
            figure = etree.SubElement(person, XmlElements.figure)
            graphic = etree.SubElement(figure, XmlElements.graphic)
            graphic.set(XmlAttributes.url, profile_image)

        return person

    def __get_person(self, person_id: str) -> etree.Element:
        """Get the person if person exists in persons list.

        Parameters
        ----------
        person_id: str, required
            The id of the person to search for.

        Returns
        -------
        person: etree.Element
            The person element if it exists; None otherwise.
        """
        for person in self.__persons_list.iterdescendants(
                tag=XmlElements.person):
            if person.get(XmlAttributes.xml_id) == person_id:
                return person

        return None
