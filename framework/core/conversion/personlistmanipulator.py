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

    def add_or_update_person(self,
                             person_id: str,
                             personal_info: PersonalInformation,
                             legislative_term: Event,
                             executive_term: Event = None):
        """Add or update person.

        Parameters
        ----------
        person_id: str, required
            The id of the person to add or update.
        personal_info: PersonalInformation, required
            The personal information.
        legislative_term: Event, required
            The legislative term in which the person appears.
        executive_term: Event, optional
            The executive term of the person. Default is None.
        """
        person_id = person_id.replace('#', '')
        person = self.__get_person(person_id)
        if person is None:
            person = self.__create_person(person_id, personal_info.first_name,
                                          personal_info.last_name,
                                          personal_info.sex,
                                          personal_info.profile_image)
            self.__sort_persons()
        self.__update_affiliation(person, legislative_term)
        if executive_term is not None:
            self.__update_affiliation(person, executive_term)

    def __sort_persons(self):
        """Sort person list by the value of id attribute."""

        def get_person_sort_key(element):
            if element.tag != XmlElements.person:
                return ''

            full_name = []
            for surname in element.iterdescendants(tag=XmlElements.surname):
                full_name.append(surname.text)
            for forename in element.iterdescendants(tag=XmlElements.forename):
                full_name.append(forename.text)

            return ' '.join(full_name)

        self.__persons_list[:] = sorted(self.__persons_list,
                                        key=get_person_sort_key)

    def __update_affiliation(self, person: etree.Element, event: Event):
        """Add the legislative term to the affiliation of the person if it doesn't exist.

        Parameters
        ----------
        person: etree.Element, required
            The person element to update.
        event: Event, required
            The event from which to extract affiliation info.
        """
        for affiliation in person.iterdescendants(tag=XmlElements.affiliation):
            if affiliation.get(XmlAttributes.ana) == event.event_id:
                # Affiliation already exists; nothing to do.
                return

        self.__add_affiliation(person, event)
        self.__sort_affiliations(person)

    def __sort_affiliations(self, person: etree.Element):
        """Sort the affiliations of the provided person by event id.

        Parameters
        ----------
        person: etree.Element, required
            The person whose affiliation to sort.
        """

        def get_affiliation_id(element):
            if element.tag != XmlElements.affiliation:
                return ''
            return element.get(XmlAttributes.ana)

        person[:] = sorted(person, key=get_affiliation_id)

    def __add_affiliation(self, person: etree.Element, event: Event):
        """Add term affiliation to the specified person.

        Parameters
        ----------
        person: etree.Element, required
            The person to which to add affilication.
        term: Event, required
            The event containing the info for affiliation.
        """
        organization_id, term_id, start_date, end_date = event
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
            surname.text = self.__capitalize_name(part)

        sex_element = etree.SubElement(person, XmlElements.sex)
        sex = sex if sex is not None else 'U'
        sex_element.set(XmlAttributes.value, sex)

        if profile_image is not None:
            figure = etree.SubElement(person, XmlElements.figure)
            graphic = etree.SubElement(figure, XmlElements.graphic)
            graphic.set(XmlAttributes.url, profile_image)

        return person

    def __capitalize_name(self, name: str) -> str:
        """Capitalize the given name.

        Parameters
        ----------
        name: str, required
            The name to capitalize.

        Returns
        -------
        capitalized_name: str
            The capitalized name.
        """
        parts = name.split(sep='-')
        return '-'.join([part.capitalize() for part in parts])

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
