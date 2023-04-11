"""Defines a class that builds the root file of the corpus."""
from .namedtuples import PersonalInformation
from .namemapping import SpeakerInfoProvider
from .organizationslistmanipulator import OrganizationsListManipulator
from .personlistmanipulator import PersonListManipulator
from .sessionspeakersreader import SessionSpeakersReader
from .xmlstats import CorpusStatsWriter
from .xmlstats import SessionStatsReader
from .xmlutils import XmlAttributes
from .xmlutils import XmlDataManipulator
from .xmlutils import XmlElements
from babel.dates import format_date
from datetime import datetime
from lxml import etree
from pathlib import Path


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
        self.__update_statistics(corpus_file)
        self.__update_speakers_list(corpus_file)
        self.__add_component_file(corpus_file)
        self.__sort_component_files()
        self.save_changes(self.__file_path)

    def __update_speakers_list(self, component_path: str):
        """Update the list of speakers with the speakers from the session transcript.

        Parameters
        ----------
        component_path: str, required
            The path of the corpus component file.
        """
        speaker_reader = SessionSpeakersReader(component_path)
        speaker_ids, gov_members = speaker_reader.get_speaker_ids()
        for speaker_id in speaker_ids:
            session_date = speaker_reader.session_date
            term = self.__org_list.get_legislative_term(session_date)
            pi = self.__speaker_info_provider.get_personal_info(speaker_id)
            profile = PersonalInformation(pi.first_name, pi.last_name, pi.sex,
                                          pi.profile_image)
            executive_term = None
            if speaker_id in gov_members:
                executive_term = self.__org_list.get_executive_term(
                    session_date)

            self.__person_list.add_or_update_person(speaker_id, profile, term,
                                                    executive_term)

    def __sort_component_files(self):
        """Sort component files by file name."""

        def get_component_path(element):
            if etree.QName(element).localname != "include":
                return ''
            return element.get("href")

        self.xml_root[:] = sorted(self.xml_root, key=get_component_path)

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
        include_element.set("href", Path(component_path).name)
        self.xml_root.append(include_element)

    def __update_statistics(self, component_path: str):
        """Update the dates and values of `tagUsage` element with the values from the corpus component file.

        Parameters
        ----------
        component_path: str, required
            The path of the corpus component file.
        """
        provider = SessionStatsReader(component_path)
        writer = CorpusStatsWriter(self.xml_root, provider)
        writer.update_statistics()
        self.__update_corpus_span(provider.get_session_date())

    def __update_corpus_span(self, session_date: datetime.date):
        """Update the date span of the corpus with the given date.

        Parameters
        ----------
        session_date: datetime.date, required
            The date of the component file session.
        """
        date_element = self.__update_span_for_element(XmlElements.setting,
                                                      session_date)
        date_element = self.__update_span_for_element(XmlElements.bibl,
                                                      session_date)
        att_from = date_element.get(XmlAttributes.event_start)
        att_to = date_element.get(XmlAttributes.event_end)
        date_element.text = f'{att_from} - {att_to}'

    def __update_span_for_element(
            self, element_name: str,
            session_date: datetime.date) -> etree.Element:
        """Update the span of the corpus with the given date for the provided element.

        Parameters
        ----------
        element_name: str, required
            The name of the element for which to update corpus span.
        session_date: datetime.date, required
            The date of the component file session.

        Returns
        -------
        date_element: etree.Element
            The child ``date`` element that contains the corpus span for further processing.
        """
        parent = next(self.xml_root.iterdescendants(tag=element_name))
        date = next(parent.iterdescendants(tag=XmlElements.date))
        start_date, end_date = datetime.max, datetime.min

        start = date.get(XmlAttributes.event_start)
        if len(start) > 0:
            start_date = datetime.fromisoformat(start)

        end = date.get(XmlAttributes.event_end)
        if len(start) > 0:
            end_date = datetime.fromisoformat(end)

        if session_date < start_date.date():
            date.set(XmlAttributes.event_start,
                     format_date(session_date, "yyyy-MM-dd"))
        if session_date > end_date.date():
            date.set(XmlAttributes.event_end,
                     format_date(session_date, "yyyy-MM-dd"))
        return date
