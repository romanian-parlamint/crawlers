"""Module responsible for conversion from JSON to  XML."""
import logging
from .jsonutils import SessionTranscript
from .xmlcreation import SessionIdBuilder
from .xmlcreation import SessionTitleBuilder
from .xmlcreation import MeetingElementContentsBuilder
from .xmlcreation import SessionIdNoBuilder
from .xmlcreation import SessionDateBuilder
from .xmlcreation import SessionSummaryBuilder
from .xmlcreation import SessionHeadingBuilder
from .xmlcreation import SessionStartEndTimeBuilder
from .xmlcreation import SessionChairmenBuilder
from .xmlcreation import SessionBodyBuilder
from typing import Dict


class SessionTranscriptConverter:
    """Convert session transcript from JSON to XML."""

    def __init__(self, input_file: str, session_template: str,
                 name_map: Dict[str, str], output_file: str):
        """Create a new instance of the class.

        Parameters
        ----------
        input_file: str, required
            The path of the session transcript in JSON format.
        session_template: str, required
            The path of the XML file containing session template.
        name_map: dict, required
            The map of speaker names to their correct names.
        output_file: str, required
            The path of the output file.
        """
        self.__input_file = input_file
        self.__session_template = session_template
        self.__name_map = name_map
        self.__output_file = output_file

    def covert(self):
        """Convert session transcript to XML format."""
        logging.info("Converting from {} to {}.".format(
            self.__input_file, self.__output_file))
        session_transcript = SessionTranscript(self.__input_file)
        self.__build_session_id(session_transcript)
        self.__build_session_title(session_transcript)
        self.__build_meeting_contents(session_transcript)
        self.__build_idno_contents(session_transcript)
        self.__build_date_contents(session_transcript)
        self.__build_session_summary(session_transcript)
        self.__build_session_heading(session_transcript)
        self.__build_session_start_time(session_transcript)
        self.__build_session_chairmen(session_transcript)
        self.__build_session_body(session_transcript)
        self.__build_session_end_time(session_transcript)

    def __build_session_body(self, session_transcript: SessionTranscript):
        """Build the session body.

        Parameters
        ----------
        session_transcript: SessionTranscript, required
            The session transcript.
        """
        builder = SessionBodyBuilder(session_transcript, self.__name_map,
                                     self.__output_file)
        builder.build_session_body()

    def __build_session_chairmen(self, session_transcript: SessionTranscript):
        """Build the node containing the information about the session chairmen.

        Parameters
        ----------
        session_transcript: SessionTranscript, required
            The session transcript.
        """
        builder = SessionChairmenBuilder(session_transcript,
                                         self.__output_file)
        builder.build_session_chairmen()

    def __build_session_end_time(self, session_transcript: SessionTranscript):
        """Build the node containing the end time of the session.

        Parameters
        ----------
        session_transcript: SessionTranscript, required
            The session transcript.
        """
        builder = SessionStartEndTimeBuilder(session_transcript,
                                             self.__output_file)
        builder.build_session_end_time()

    def __build_session_start_time(self,
                                   session_transcript: SessionTranscript):
        """Build the node containing end time of the session.

        Parameters
        ----------
        session_transcript: SessionTranscript, required
            The session transcript.
        """
        builder = SessionStartEndTimeBuilder(session_transcript,
                                             self.__output_file)
        builder.build_session_start_time()

    def __build_session_heading(self, session_transcript: SessionTranscript):
        """Build the session heading.

        Parameters
        ----------
        session_transcript: SessionTranscript, required
            The session transcript.
        """
        builder = SessionHeadingBuilder(session_transcript, self.__output_file)
        builder.build_session_heading()

    def __build_session_summary(self, session_transcript: SessionTranscript):
        """Build the session summary.

        Parameters
        ----------
        session_transcript: SessionTranscript, required
            The session transcript.
        """
        builder = SessionSummaryBuilder(session_transcript, self.__output_file)
        builder.build_summary()

    def __build_date_contents(self, session_transcript: SessionTranscript):
        """Build contents of date elements.

        Parameters
        ----------
        session_transcript: SessionTranscript, required
            The session transcript.
        """
        builder = SessionDateBuilder(session_transcript, self.__output_file)
        builder.build_date_contents()

    def __build_idno_contents(self, session_transcript: SessionTranscript):
        """Build idno element.

        Parameters
        ----------
        session_transcript: SessionTranscript, required
            The session transcript.
        """
        builder = SessionIdNoBuilder(session_transcript, self.__output_file)
        builder.build_session_idno()

    def __build_meeting_contents(self, session_transcript: SessionTranscript):
        """Build meeting element.

        Parameters
        ----------
        session_transcript: SessionTranscript, required
            The session transcript.
        """
        builder = MeetingElementContentsBuilder(session_transcript,
                                                self.__output_file)
        builder.build_meeting_info()

    def __build_session_title(self, session_transcript: SessionTranscript):
        """Build session title.

        Parameters
        ----------
        session_transcript: SessionTranscript, required
            The session transcript.
        """
        builder = SessionTitleBuilder(session_transcript, self.__output_file)
        builder.build_session_title()

    def __build_session_id(self, session_transcript: SessionTranscript):
        """Build session id.

        Parameters
        ----------
        session_transcript: SessionTranscript, required
            The session transcript.
        """
        session_id_builder = SessionIdBuilder(self.__input_file,
                                              self.__session_template,
                                              session_transcript,
                                              self.__output_file)
        session_id_builder.build_session_id()
