"""Utility components for JSON files."""
import json
import datetime
from typing import List


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

    @property
    def start_mark(self) -> str:
        """Get the start mark of the session."""
        start = self.__json['start']
        if start is None:
            return None
        return start['start_mark']

    @property
    def end_mark(self) -> str:
        """Get the end mark of the session."""
        end = self.__json['end']
        if end is None:
            return None
        return end['end_mark']

    @property
    def chairman(self) -> str:
        """Get the session chairman."""
        start = self.__json['start']
        if start is None:
            return None
        return start['chairmen']

    @property
    def body(self):
        """Get the session body from the transcript."""
        return [BodySegment(segment) for segment in self.__json['sections']]


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
    def contents(self) -> List[SummaryContentLine]:
        """Get the contents of the summary segment.

        Returns
        -------
        contents: iterable of SummarySegmentContents
            The contents of the session summary segment.
        """
        return [SummaryContentLine(c) for c in self.__segment['contents']]


class Speaker:
    """Encapsulates speaker information."""

    def __init__(self, speaker: dict):
        """Create a new instance of the class."""
        self.__speaker = speaker if speaker is not None else {
            "text": None,
            "full_name": None,
            "profile_url": None,
            "sex": None,
            "annotation": None
        }
        self.__is_empty = True if speaker is None else False

    @property
    def full_name(self) -> str:
        """Get the full name of the speaker."""
        return self.__speaker['full_name']

    @property
    def announcement(self) -> str:
        """Get the text which announces the speaker."""
        return self.__speaker['text']

    @property
    def is_empty(self) -> bool:
        """Return True if the speaker is empty; otherwise False."""
        return self.__is_empty


class SessionContentLine:
    """Encapsulates a content line from the session transcript."""

    def __init__(self, content_line):
        """Create a new instance of the class."""
        self.__content = content_line if content_line is not None else {
            'text': None,
            'annotations': []
        }

    @property
    def text(self) -> str:
        """Get the text of the content line."""
        return self.__content['text']

    @property
    def annotations(self) -> List[str]:
        """Get the annotations of the content line."""
        return self.__content['annotations']

    @property
    def is_empty(self) -> bool:
        """Return True if content line is empty; otherwise False."""
        no_text = self.text is None or len(self.text) == 0
        return no_text and len(self.annotations) == 0


class BodySegment:
    """Encapsulates a segment of the session body."""

    def __init__(self, segment):
        """Create a new instance of the class."""
        self.__segment = segment

    @property
    def speaker(self) -> Speaker:
        """Get the speaker of the segment."""
        return Speaker(self.__segment['speaker'])

    @property
    def contents(self) -> List[SessionContentLine]:
        """Get the contents of the segment."""
        return [
            SessionContentLine(line) for line in self.__segment['contents']
        ]

    @property
    def is_empty(self) -> bool:
        """Return True if the current segment is empty; otherwise False."""
        return self.__segment['speaker'] is None and len(
            self.__segment['contents']) == 0
