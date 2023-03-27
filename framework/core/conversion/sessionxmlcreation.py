"""Module responsible for creating XML elements."""
from babel.dates import format_date
from lxml import etree
from typing import List
from .jsonutils import SessionTranscript
from .jsonutils import BodySegment
from .jsonutils import Speaker
from .xmlutils import XmlDataManipulator
from .xmlutils import XmlAttributes
from .xmlutils import XmlElements
from .xmlutils import Resources
from .namemapping import SpeakerInfoProvider


class SessionIdBuilder(XmlDataManipulator):
    """Builds the session id."""

    def __init__(self, template_file: str, transcript: SessionTranscript,
                 output_file: str):
        """Create a new instance of the class.

        Parameters
        ----------
        template_file: str, required
            The path of the session template file.
        transcript: SessionTranscript, required
        output_file, str, required
            The path of the output XML file.
        """
        XmlDataManipulator.__init__(self, template_file)
        self.__transcript = transcript
        self.__output_file = output_file

    def build_session_id(self):
        """Build session id and save file."""
        xml_id = "ParlaMint-RO_{}-id{}".format(self.__transcript.session_date,
                                               self.__transcript.session_id)
        self.xml_root.set(XmlAttributes.xml_id, xml_id)
        self.save_changes(self.__output_file)


class JsonTranscriptToXmlConverter(XmlDataManipulator):
    """Base class for converting JSON transcript to XML.""" ""

    def __init__(self, session_transcript: SessionTranscript, xml_file: str):
        """Create a new instance of the class.

        Parameters
        ----------
        session_transcript: SessionTranscript, required
            The session transcript.
        xml_file: str, required
            The file containing session transcript in XML format.
        """
        XmlDataManipulator.__init__(self, xml_file)
        self.__transcript = session_transcript

    @property
    def session_transcript(self) -> SessionTranscript:
        """Get the session transcript.""" ""
        return self.__transcript


class SessionTitleBuilder(JsonTranscriptToXmlConverter):
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
        JsonTranscriptToXmlConverter.__init__(self, session_transcript,
                                              xml_file)

    def build_session_title(self, add_sample_tag: bool = False):
        """Build session title.

        Parameters
        ----------
        add_sample_tag: bool, optional
            Instructs the builder to add sample tag when true.
        """
        session_date = self.session_transcript.session_date
        ro_date = format_date(session_date, "d MMMM yyyy", locale="ro")
        en_date = format_date(session_date, "MMMM d yyyy", locale="en")

        for elem in self.xml_root.iterdescendants(tag=XmlElements.title):
            if elem.getparent().tag != XmlElements.titleStmt:
                continue

            title_type = elem.get(XmlAttributes.element_type)
            lang = elem.get(XmlAttributes.lang)
            if title_type == 'main' and lang == 'ro':
                elem.text = Resources.SessionTitleRo.format(ro_date)
                if add_sample_tag:
                    elem.text = elem.text + ' [ParlaMint SAMPLE]'

            if title_type == 'main' and lang == 'en':
                elem.text = Resources.SessionTitleEn.format(en_date)
                if add_sample_tag:
                    elem.text = elem.text + ' [ParlaMint SAMPLE]'

            if title_type == 'sub' and lang == 'ro':
                elem.text = Resources.SessionSubtitleRo.format(ro_date)

            if title_type == 'sub' and lang == 'en':
                elem.text = Resources.SessionSubtitleEn.format(en_date)

        self.save_changes()


class MeetingElementContentsBuilder(JsonTranscriptToXmlConverter):
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
        JsonTranscriptToXmlConverter.__init__(self, session_transcript,
                                              xml_file)

    def build_meeting_info(self):
        """Build meeting element contents."""
        session_date = self.session_transcript.session_date
        meeting_n = format_date(session_date, "yyyyMMdd")

        for meeting in self.xml_root.iterdescendants(tag=XmlElements.meeting):
            meeting.set(XmlAttributes.meeting_n, meeting_n)

        self.save_changes()


class SessionIdNoBuilder(JsonTranscriptToXmlConverter):
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
        JsonTranscriptToXmlConverter.__init__(self, session_transcript,
                                              xml_file)

    def build_session_idno(self):
        """Build the contents of the idno element."""
        for idno in self.xml_root.iterdescendants(tag=XmlElements.idno):
            if idno.get(XmlAttributes.element_type) == 'URI':
                idno.text = self.session_transcript.transcript_url

        self.save_changes()


class SessionDateBuilder(JsonTranscriptToXmlConverter):
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
        JsonTranscriptToXmlConverter.__init__(self, session_transcript,
                                              xml_file)

    def build_date_contents(self):
        """Build the content of date elements."""
        session_date = self.session_transcript.session_date
        for date in self.xml_root.iterdescendants(tag=XmlElements.date):
            parent_tag = date.getparent().tag
            if parent_tag == XmlElements.setting or parent_tag == XmlElements.bibl:
                date.set(XmlAttributes.when,
                         format_date(session_date, "yyyy-MM-dd"))
                date.text = format_date(session_date, "dd.MM.yyyy")

        self.save_changes()


class DebateSectionBuilder(JsonTranscriptToXmlConverter):
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
        JsonTranscriptToXmlConverter.__init__(self, session_transcript,
                                              xml_file)
        self.__debate_section = None

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

        for div in self.xml_root.iterdescendants(XmlElements.div):
            if div.get(XmlAttributes.element_type) == "debateSection":
                self.__debate_section = div
                return self.__debate_section


class SessionSummaryBuilder(DebateSectionBuilder):
    """Builds the session summary."""

    def build_summary(self):
        """Build the summary of the session."""
        self.__build_summary_heading()

        if len(self.session_transcript.summary) > 0:
            self.__build_table_of_contents()

        self.save_changes()

    def __build_table_of_contents(self):
        """Build the table of contents using summary elements."""
        self.__build_note("editorial", Resources.ToC)

        for summary_line in self.session_transcript.summary:
            for content in summary_line.contents:
                text = content.text
                if isinstance(text, str):
                    self.__build_note("summary", text)
                else:
                    for line in text:
                        self.__build_note("summary", line)

    def __build_note(self, note_type: str, text: str):
        """Build a child note element.

        Parameters
        ----------
        note_type: str, required
            The type of the note.
        text: str, required
            The text of the note.
        """
        note = etree.SubElement(self.debate_section, XmlElements.note)
        note.set(XmlAttributes.element_type, note_type)
        note.text = text

    def __build_summary_heading(self):
        """Build the heading nodes of the summary."""
        head = etree.SubElement(self.debate_section, XmlElements.head)
        head.text = Resources.Heading

        session_head = etree.SubElement(self.debate_section, XmlElements.head)
        session_head.set(XmlAttributes.element_type, "session")
        session_date = self.session_transcript.session_date
        session_date = format_date(session_date, "d MMMM yyyy")
        session_head.text = Resources.SessionHeading.format(session_date)


class SessionHeadingBuilder(DebateSectionBuilder):
    """Builds the session heading."""

    def build_session_heading(self):
        """Build the session heading."""
        session_title = self.session_transcript.session_title
        if session_title is None:
            return
        note = etree.SubElement(self.debate_section, XmlElements.note)
        note.set(XmlAttributes.element_type, "editorial")
        note.text = session_title
        self.save_changes()


class SessionStartEndTimeBuilder(DebateSectionBuilder):
    """Builds the note elements containing the session start/end time."""

    def build_session_start_time(self):
        """Build session start time note."""
        start_time = self.session_transcript.start_mark
        if start_time is None:
            return

        note = etree.SubElement(self.debate_section, XmlElements.note)
        note.set(XmlAttributes.element_type, "time")
        note.text = start_time
        self.save_changes()

    def build_session_end_time(self):
        """Build session end time note."""
        end_time = self.session_transcript.end_mark
        if end_time is None:
            return

        note = etree.SubElement(self.debate_section, XmlElements.note)
        note.set(XmlAttributes.element_type, "time")
        note.text = end_time
        self.save_changes()


class SessionChairmenBuilder(DebateSectionBuilder):
    """Builds the node containing info about the chairmen of the session."""

    def build_session_chairmen(self):
        """Build the node containing session chairmen."""
        chairman = self.session_transcript.chairman
        if chairman is None:
            return

        note = etree.SubElement(self.debate_section, XmlElements.note)
        note.set(XmlAttributes.element_type, "narrative")
        note.text = chairman
        self.save_changes()


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
                 speaker_info_provider: SpeakerInfoProvider, xml_file: str):
        """Create a new instance of the class.

        Parameters
        ----------
        session_transcript: SessionTranscript, required
            The session transcript.
        xml_file: str, required
            The file containing session transcript in XML format.
        speaker_info_provider: SpeakerInfoProvider, required
            An instance of SpeakerInfoProvider used for building speaker id.
        """
        super().__init__(session_transcript, xml_file)
        self.__element_id_builder = SessionElementsIdBuilder(self.xml_root)
        self.__speaker_info_provider = speaker_info_provider

    def build_session_body(self):
        """Build the session body."""
        session_segments = self.session_transcript.body
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
        self.save_changes()

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
        seg.set(XmlAttributes.xml_id,
                self.__element_id_builder.get_segment_id())
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
        speaker_id = self.__speaker_info_provider.get_speaker_id(speaker_name)
        utterance.set(XmlAttributes.who, speaker_id)
        utterance.set(XmlAttributes.xml_id,
                      self.__element_id_builder.get_utterance_id())
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

        return self.__speaker_info_provider.get_speaker_name(speaker.full_name)
