"""Module responsible for creating XML elements."""
from .jsonutils import SessionWrapper
from .xmlutils import load_xml, XmlAttributes, save_xml


class SessionIdBuilder:
    """Builds the session id."""

    def __init__(self, input_file: str, template_file: str, output_file: str):
        """Create a new instance of the class.

        Parameters
        ----------
        input_file: str, required
            The path of the JSON file containing session transcript.
        template_file: str, required
            The path of the session template file.
        output_file, str, required
            The path of the output XML file.
        """
        self.__input_file = input_file
        self.__template_file = template_file
        self.__output_file = output_file

    def build_session_id(self):
        """Build session id and save file."""
        transcript = SessionWrapper(self.__input_file)
        xml_root = load_xml(self.__template_file)
        xml_id = "ParlaMint-RO-{}-{}".format(transcript.session_date,
                                             transcript.session_id)
        xml_root.getroot().set(XmlAttributes.xml_id, xml_id)
        save_xml(xml_root, self.__output_file)
