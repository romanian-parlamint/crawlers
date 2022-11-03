"""Module responsible for creating XML elements."""
from babel.dates import format_date
from .jsonutils import SessionTranscript
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
