"""Utility components for JSON files."""
import json
import datetime


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
