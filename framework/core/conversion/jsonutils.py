"""Utility components for JSON files."""
import json
import datetime
from typing import Iterable


class SessionTranscript:
    """Ecapsulates session transcription JSON."""

    def __init__(self, input_file):
        """Create a new instance of the class.

        Parameters
        ----------
        input_file: str, required
            The path of the JSON file containing session transcript.
        """
        self.__json = load_json(input_file)

    @property
    def session_id(self):
        """Get the session id."""
        return self.__json['session_id']

    @property
    def session_title(self) -> str:
        """Get the session title."""
        return self.__json['session_title']

    @property
    def session_date(self):
        """Get the session date."""
        session_start = self.__json['start']
        if session_start is None:
            raise ValueError(
                "Start section of session transcription not found.")
        start_time = session_start['start_time']
        if start_time is None:
            raise ValueError("Start time of session not found.")

        start_time = datetime.datetime.fromisoformat(start_time)
        return start_time.date()

    @property
    def transcript_url(self):
        """Get the transcript URL."""
        return self.__json['full_transcript_url']

    @property
    def summary(self):
        """Get the summary section from session transcript."""
        return [SummarySegment(segment) for segment in self.__json['summary']]


def load_json(file_name: str) -> dict:
    """Load  the JSON file.

    Parameters
    ----------
    file_name: str, required
        The JSON file.

    Returns
    -------
    contents: dict
        The contents of the JSON file.
    """
    with open(file_name, 'r') as f:
        return json.load(f)


class SummaryContentLine:
    """Encapsulates a content line of a summary segment."""

    def __init__(self, content_line: dict):
        """Create a new  instance of the class.

        Parameters
        ----------
        content_line: dict, required
            The dictionary with content line.
        """
        self.__line = content_line

    @property
    def text(self) -> str:
        """Get the text of the content line.

        Returns
        -------
        text: str
            The text of the content line.
        """
        return self.__line['line_contents']

    @property
    def annotation(self) -> str:
        """Get the annotation of the content line.

        Returns
        -------
        annotation: str
            The annotation text.
        """
        return self.__line['annotation']


class SummarySegment:
    """Encapsulates a segment of session summary."""

    def __init__(self, summary_segment: dict):
        """Create a new instance of the class."""
        self.__segment = summary_segment

    @property
    def number(self) -> int:
        """Get the order number of the current segment.

        Returns
        -------
        number: int
            The order number of the segment.
        """
        return int(self.__segment['number'])

    @property
    def contents(self) -> Iterable[SummaryContentLine]:
        """Get the contents of the summary segment.

        Returns
        -------
        contents: iterable of SummarySegmentContents
            The contents of the session summary segment.
        """
        return [SummaryContentLine(c) for c in self.__segment['contents']]
