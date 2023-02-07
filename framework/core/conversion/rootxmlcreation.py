"""Module responsible for creating root XML files."""
from .namemapping import SpeakerInfoProvider
from .xmlstats import CorpusStatsWriter
from .xmlstats import SessionStatsReader
from .xmlutils import XmlDataManipulator
from .xmlutils import XmlElements, XmlAttributes
from collections import namedtuple
from datetime import date
from datetime import datetime
from lxml import etree
from typing import Generator
from typing import List
from typing import Tuple
import logging


class RootCorpusFileBuilder(XmlDataManipulator):
    """Builds the root file of the corpus."""

    def __init__(self,
                 file_path: str,
                 template_file: str,
                 speaker_info_provider: SpeakerInfoProvider,
                 append: bool = False):
        """Create a new instance of the class.

        Parameters
        ----------
        file_path: str, required
            The path of the corpus root file.
        template_file: str, required
            The path of the corpus root template file.
        speaker_info_provider: SpeakerInfoProvider, required
            An instance of SpeakerInfoProvider used for filling speaker info.
        append: bool, optional
            A flag indicating whether to append to existing file or to start from scratch.
        """
        root_file = file_path if append else template_file
        XmlDataManipulator.__init__(self, root_file)
        self.__file_path = file_path
        self.__speaker_info_provider = speaker_info_provider
        self.__person_list = PersonListManipulator(self.xml_root)
        self.__org_list = OrganizationsListManipulator(self.xml_root)

    def add_corpus_file(self, corpus_file: str):
        """Add the specified file to the corpus root file.

        Parameters
        ----------
        corpus_file: str, required
            The path of the file to add to the corpus.
        """
        self.__update_tag_usage(corpus_file)
        self.__update_speakers_list(corpus_file)
        self.__add_component_file(corpus_file)
        self.save_changes(self.__file_path)

    def __update_speakers_list(self, component_path: str):
        """Update the list of speakers with the speakers from the session transcript.

        Parameters
        ----------
        component_path: str, required
            The path of the corpus component file.
        """
        speaker_reader = SessionSpeakersReader(component_path)
        for speaker_id in speaker_reader.get_speaker_ids():
            session_date = speaker_reader.session_date
            term = self.__org_list.get_legislative_term(session_date)
            pi = self.__speaker_info_provider.get_personal_info(speaker_id)
            self.__person_list.add_or_update_person(
                speaker_id, term,
                PersonalInformation(pi.first_name, pi.last_name, pi.sex,
                                    pi.profile_image))

    def __add_component_file(self, component_path: str):
        """Add the component path to the `include` element.

        Parameters
        ----------
        component_path: str, required
            The path of the corpus component file.
        """
        etree.register_namespace("xsi", "http://www.w3.org/2001/XInclude")
        qname = etree.QName("http://www.w3.org/2001/XInclude", "include")
        include_element = etree.Element(qname)
        include_element.set("href", component_path)
        self.xml_root.append(include_element)

    def __update_tag_usage(self, component_path: str):
        """Update the values of `tagUsage` element with the values from the corpus component file.

        Parameters
        ----------
        component_path: str, required
            The path of the corpus component file.
        """
        provider = SessionStatsReader(component_path)
        writer = CorpusStatsWriter(self.xml_root, provider)
        writer.update_statistics()


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
        return (None, None, None)

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


Term = namedtuple('Term', ['org_id', 'term_id', 'start_date', 'end_date'])
PersonalInformation = namedtuple(
    'PersonalInformation', ["first_name", "last_name", "sex", "profile_image"])


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

    def add_or_update_person(self, person_id: str, legislative_term: Term,
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
                             legislative_term: Term):
        """Add the legislative term to the affiliation of the person if it doesn't exist.

        Parameters
        ----------
        person: etree.Element, required
            The person element to update.
        legislative_term: tuple of (str, str, date, date), required
            The id, organization id, start date, and end date of the legislative term.
        """
        term_id, organization_id, start_date, end_date = legislative_term
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
        sex_element.text = sex

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
