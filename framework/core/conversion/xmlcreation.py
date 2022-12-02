"""Module responsible for creating XML elements."""
from babel.dates import format_date
from lxml import etree
from typing import List
from typing import Dict
from .jsonutils import SessionTranscript
from .jsonutils import BodySegment
from .jsonutils import Speaker
from .xmlutils import load_xml
from .xmlutils import save_xml
from .xmlutils import XmlAttributes
from .xmlutils import XmlElements
from .xmlutils import Resources


class SessionIdBuilder:
    """Builds the session id."""

    def __init__(self, input_file: str, template_file: str,
                 transcript: SessionTranscript, output_file: str):
        """Create a new instance of the class.

        Parameters
        ----------
        input_file: str, required
            The path of the JSON file containing session transcript.
        template_file: str, required
            The path of the session template file.
        transcript: SessionTranscript, required
        output_file, str, required
            The path of the output XML file.
        """
        self.__input_file = input_file
        self.__template_file = template_file
        self.__transcript = transcript
        self.__output_file = output_file

    def build_session_id(self):
        """Build session id and save file."""
        xml_root = load_xml(self.__template_file)
        xml_id = "ParlaMint-RO-{}-{}".format(self.__transcript.session_date,
                                             self.__transcript.session_id)
        xml_root.getroot().set(XmlAttributes.xml_id, xml_id)
        save_xml(xml_root, self.__output_file)


class SessionTitleBuilder:
    """Builds the session title."""

    def __init__(self, session_transcript: SessionTranscript, xml_file: str):
        """Create a new instance of the class.

        Parameters
        ----------
        session_transcript: SessionTranscript, required
            The session transcript.
        xml_file: str, required
            The file containing session transcript in XML format.
        """
        self.__transcript = session_transcript
        self.__xml_file = xml_file
        self.__xml_root = load_xml(xml_file)

    @property
    def xml(self):
        """Get the root node of the XML."""
        return self.__xml_root.getroot()

    def build_session_title(self):
        """Build session title."""
        session_date = self.__transcript.session_date
        ro_date = format_date(session_date, "d MMMM yyyy", locale="ro")
        en_date = format_date(session_date, "MMMM d yyyy", locale="en")

        for elem in self.xml.iterdescendants(tag=XmlElements.title):
            if elem.getparent().tag != XmlElements.titleStmt:
                continue

            title_type = elem.get(XmlAttributes.element_type)
            lang = elem.get(XmlAttributes.lang)
            if title_type == 'main' and lang == 'ro':
                elem.text = Resources.SessionTitleRo.format(ro_date)

            if title_type == 'main' and lang == 'en':
                elem.text = Resources.SessionTitleEn.format(en_date)

            if title_type == 'sub' and lang == 'ro':
                elem.text = Resources.SessionSubtitleRo.format(ro_date)

            if title_type == 'sub' and lang == 'en':
                elem.text = Resources.SessionSubtitleEn.format(en_date)

        save_xml(self.__xml_root, self.__xml_file)


class MeetingElementContentsBuilder:
    """Builds the contents of the meeting elements."""

    def __init__(self, session_transcript: SessionTranscript, xml_file: str):
        """Create a new instance of the class.

        Parameters
        ----------
        session_transcript: SessionTranscript, required
            The session transcript.
        xml_file: str, required
            The file containing session transcript in XML format.
        """
        self.__transcript = session_transcript
        self.__xml_file = xml_file
        self.__xml_root = load_xml(xml_file)

    @property
    def xml(self):
        """Get the root node of the XML."""
        return self.__xml_root.getroot()

    def build_meeting_info(self):
        """Build meeting element contents."""
        session_date = self.__transcript.session_date
        meeting_n = format_date(session_date, "yyyyMMdd")

        for meeting in self.xml.iterdescendants(tag=XmlElements.meeting):
            meeting.set(XmlAttributes.meeting_n, meeting_n)

        save_xml(self.__xml_root, self.__xml_file)


class SessionIdNoBuilder:
    """Builds the idno element."""

    def __init__(self, session_transcript: SessionTranscript, xml_file: str):
        """Create a new instance of the class.

        Parameters
        ----------
        session_transcript: SessionTranscript, required
            The session transcript.
        xml_file: str, required
            The file containing session transcript in XML format.
        """
        self.__transcript = session_transcript
        self.__xml_file = xml_file
        self.__xml_root = load_xml(xml_file)

    @property
    def xml(self):
        """Get the root node of the XML."""
        return self.__xml_root.getroot()

    def build_session_idno(self):
        """Build the contents of the idno element."""
        for idno in self.xml.iterdescendants(tag=XmlElements.idno):
            if idno.get(XmlAttributes.element_type) == 'URI':
                idno.text = self.__transcript.transcript_url
        save_xml(self.__xml_root, self.__xml_file)


class SessionDateBuilder:
    """Builds the contents of date elements."""

    def __init__(self, session_transcript: SessionTranscript, xml_file: str):
        """Create a new instance of the class.

        Parameters
        ----------
        session_transcript: SessionTranscript, required
            The session transcript.
        xml_file: str, required
            The file containing session transcript in XML format.
        """
        self.__transcript = session_transcript
        self.__xml_file = xml_file
        self.__xml_root = load_xml(xml_file)

    @property
    def xml(self):
        """Get the root node of the XML."""
        return self.__xml_root.getroot()

    def build_date_contents(self):
        """Build the content of date elements."""
        session_date = self.__transcript.session_date
        for date in self.xml.iterdescendants(tag=XmlElements.date):
            parent_tag = date.getparent().tag
            if parent_tag == XmlElements.setting or parent_tag == XmlElements.bibl:
                date.set(XmlAttributes.when,
                         format_date(session_date, "yyyy-MM-dd"))
                date.text = format_date(session_date, "dd.MM.yyyy")

        save_xml(self.__xml_root, self.__xml_file)


class DebateSectionBuilder:
    """A builder that works on the debate section."""

    def __init__(self, session_transcript: SessionTranscript, xml_file: str):
        """Create a new instance of the class.

        Parameters
        ----------
        session_transcript: SessionTranscript, required
            The session transcript.
        xml_file: str, required
            The file containing session transcript in XML format.
        """
        self.__transcript = session_transcript
        self.__xml_file = xml_file
        self.__xml_root = load_xml(xml_file)
        self.__debate_section = None

    @property
    def transcript(self) -> SessionTranscript:
        """Get the session transcript.

        Returns
        -------
        transcript: SessionTranscript
            The session transcript.
        """
        return self.__transcript

    @property
    def xml(self) -> etree.Element:
        """Get the root node of the XML."""
        return self.__xml_root.getroot()

    @property
    def debate_section(self) -> etree.Element:
        """Get the debate section of the XML.

        Returns
        -------
        debate_section, Element
            The debate section element.
        """
        if self.__debate_section is not None:
            return self.__debate_section

        for div in self.xml.iterdescendants(XmlElements.div):
            if div.get(XmlAttributes.element_type) == "debateSection":
                self.__debate_section = div
                return self.__debate_section

    def save_xml(self):
        """Save the xml contents."""
        save_xml(self.__xml_root, self.__xml_file)


class SessionSummaryBuilder(DebateSectionBuilder):
    """Builds the session summary."""

    def build_summary(self):
        """Build the summary of the session."""
        self.__build_summary_heading()

        if len(self.transcript.summary) > 0:
            self.__build_table_of_contents()

        self.save_xml()

    def __build_table_of_contents(self):
        """Build the table of contents using summary elements."""
        note = etree.SubElement(self.debate_section, XmlElements.note)
        note.set(XmlAttributes.element_type, "editorial")
        note.text = Resources.ToC

        for summary_line in self.transcript.summary:
            for content in summary_line.contents:
                note = etree.SubElement(self.debate_section, XmlElements.note)
                note.set(XmlAttributes.element_type, "summary")
                note.text = content.text

    def __build_summary_heading(self):
        """Build the heading nodes of the summary."""
        head = etree.SubElement(self.debate_section, XmlElements.head)
        head.text = Resources.Heading

        session_head = etree.SubElement(self.debate_section, XmlElements.head)
        session_head.set(XmlAttributes.element_type, "session")
        session_date = self.transcript.session_date
        session_date = format_date(self.transcript.session_date, "d MMMM yyyy")
        session_head.text = Resources.SessionHeading.format(session_date)


class SessionHeadingBuilder(DebateSectionBuilder):
    """Builds the session heading."""

    def build_session_heading(self):
        """Build the session heading."""
        session_title = self.transcript.session_title
        if session_title is None:
            return
        note = etree.SubElement(self.debate_section, XmlElements.note)
        note.set(XmlAttributes.element_type, "editorial")
        note.text = session_title
        self.save_xml()


class SessionStartEndTimeBuilder(DebateSectionBuilder):
    """Builds the note elements containing the session start/end time."""

    def build_session_start_time(self):
        """Build session start time note."""
        start_time = self.transcript.start_mark
        if start_time is None:
            return

        note = etree.SubElement(self.debate_section, XmlElements.note)
        note.set(XmlAttributes.element_type, "time")
        note.text = start_time
        self.save_xml()

    def build_session_end_time(self):
        """Build session end time note."""
        end_time = self.transcript.end_mark
        if end_time is None:
            return

        note = etree.SubElement(self.debate_section, XmlElements.note)
        note.set(XmlAttributes.element_type, "time")
        note.text = end_time
        self.save_xml()


class SessionChairmenBuilder(DebateSectionBuilder):
    """Builds the node containing info about the chairmen of the session."""

    def build_session_chairmen(self):
        """Build the node containing session chairmen."""
        chairman = self.transcript.chairman
        if chairman is None:
            return

        note = etree.SubElement(self.debate_section, XmlElements.note)
        note.set(XmlAttributes.element_type, "chairman")
        note.text = chairman
        self.save_xml()


class SessionElementsIdBuilder:
    """Builds the xml:id attribute for session elements.""" ""

    def __init__(self, xml_root: etree.Element):
        """Create a new instance of the class.

        Parameters
        ----------
        xml_root: etree.Element, required
            The root element of the session XML.
        """ ""
        self.__session_id = xml_root.get(XmlAttributes.xml_id)
        self.__utterance_id = 0
        self.__segment_id = 0

    def get_utterance_id(self) -> str:
        """Get the next id of an 'u' element.

        Returns
        -------
        utterance_id: str
            The id of the utterance element.
        """
        self.__utterance_id += 1
        self.__segment_id = 0
        return "{session}.u{utterance}".format(session=self.__session_id,
                                               utterance=self.__utterance_id)

    def get_segment_id(self) -> str:
        """Get the id of a 'seg' element.

        Returns
        -------
        segment_id: str
            The id of the segment element.
        """ ""
        self.__segment_id += 1
        return "{session}.u{utterance}.seg{segment}".format(
            session=self.__session_id,
            utterance=self.__utterance_id,
            segment=self.__segment_id)


class SessionBodyBuilder(DebateSectionBuilder):
    """Builds the nodes containing the session body."""

    def __init__(self, session_transcript: SessionTranscript,
                 speaker_name_map: Dict[str, str], xml_file: str):
        """Create a new instance of the class.

        Parameters
        ----------
        session_transcript: SessionTranscript, required
            The session transcript.
        xml_file: str, required
            The file containing session transcript in XML format.
        """
        super().__init__(session_transcript, xml_file)
        self.__name_map = speaker_name_map
        self.__id_builder = SessionElementsIdBuilder(self.xml)

    def build_session_body(self):
        """Build the session body."""
        session_segments = self.transcript.body
        if len(session_segments) == 0:
            return

        chairman = self.__get_speaker(session_segments, 0)
        chairman_name = self.__get_speaker_name(chairman)
        for idx, segment in enumerate(session_segments):
            if segment.is_empty:
                continue

            speaker = self.__get_speaker(session_segments, idx)
            speaker_name = self.__get_speaker_name(speaker)

            self.__build_speaker_note(speaker.announcement)
            utterance = self.__build_utterance(speaker_name, chairman_name)
            for content_line in segment.contents:
                if content_line.is_empty:
                    continue
                self.__build_segment(utterance, content_line.text)

            # TODO: Add editorial/gap elements if present
            # TODO: Map speaker name from the file
        self.save_xml()

    def __build_segment(self, utterance: etree.Element, text: str):
        """Build a segment element and add it to the parent utterance element.

        Parameters
        ----------
        utterance: etree.Element, required
            The parent utterance element.
        text: str, required
            The text of the segment.
        """ ""
        seg = etree.SubElement(utterance, XmlElements.seg)
        seg.set(XmlAttributes.xml_id, self.__id_builder.get_segment_id())
        seg.text = text

    def __build_utterance(self, speaker_name: str, chairman_name: str):
        """Build an utterance element and add it to the debate section.

        Parameters
        ----------
        speaker_name: str, required
            The name of the speaker.
        chairman_name: str, required
            The name of the session chairman.

        Returns
        -------
        utterance: etree.Element
            The utterance element.
        """
        utterance = etree.SubElement(self.debate_section, XmlElements.u)
        speaker_type = "#chair" if speaker_name == chairman_name else "#regular"
        utterance.set(XmlAttributes.ana, speaker_type)
        # TODO: Build speaker id
        utterance.set(XmlAttributes.who, speaker_name)
        utterance.set(XmlAttributes.xml_id,
                      self.__id_builder.get_utterance_id())
        return utterance

    def __build_speaker_note(self, text: str):
        """Build a speaker note element and add it to the debate section.

        Parameters
        ----------
        text: str, required
            The text of the note.
        """
        note = etree.SubElement(self.debate_section, XmlElements.note)
        note.set(XmlAttributes.element_type, "speaker")
        note.text = text

    def __get_speaker(self, session_segments: List[BodySegment],
                      segment_index: int) -> Speaker:
        """Get the speaker for the segment at the specified index.

        Parameters
        ----------
        session_segments: list of BodySegment, required
            The session segments.
        segment_index: int, required
            The index of the segment for which to determine the speaker.

        Returns
        -------
        speaker: Speaker
            The speaker associated with the current segment.
        """
        # Iterate backwards from the current index until the first speaker that is not None
        while (segment_index >= 0):
            segment = session_segments[segment_index]
            speaker = segment.speaker
            if (speaker is not None) and (not speaker.is_empty):
                return speaker
            segment_index = segment_index - 1

        raise ValueError("Could not determine speaker.")

    def __get_session_chairman(self,
                               session_segments: List[BodySegment]) -> Speaker:
        """Get the chairman of the session from session segments.

        Parameters
        ----------
        session_segments: list of BodySegment, required
            The session segments.

        Returns
        -------
        chairman_name: Speaker
            The session chairman.
        """
        # The chairman is the first speaker of the session
        for segment in session_segments:
            if segment.speaker is not None:
                return segment.speaker
        raise ValueError("Could not determine the chairman of the session.")

    def __get_speaker_name(self, speaker: Speaker) -> str:
        """Get the speaker name from the provided segment.

        Parameters
        ----------
        speaker: Speaker, required
            The speaker of the session segment.

        Returns
        -------
        speaker_name: str
            The name of the speaker if found; None otherwise.
        """
        if speaker is None:
            return None

        if speaker.full_name in self.__name_map:
            return self.__name_map[speaker.full_name]

        return speaker.full_name
