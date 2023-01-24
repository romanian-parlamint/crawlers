"""Module responsible for mapping speaker names to their information."""
import logging
import re
from typing import Dict
from unidecode import unidecode


class SpeakerInfoProvider:
    """Provides speaker info."""

    def __init__(self, name_map: Dict[str, str]):
        """Create a new instance of the class.

        Parameters
        ----------
        name_map: dict of (str, str), required
            The dictionary mapping names as they appear in JSON transcriptions to the correct names of speakers.
        """
        self.__name_map = {
            unidecode(k.lower()): v
            for k, v in name_map.items()
        }
        self.__id_map = {}
        self.__translations = str.maketrans({' ': '-'})

    def get_speaker_id(self, speaker_name: str) -> str:
        """Get the speaker id from the provided full name of the speaker.

        Parameters
        ----------
        speaker_name: str, required
            The full name of the speaker.

        Returns
        -------
        speaker_id: str
            The id of the speaker.
        """
        normalized_name = unidecode(speaker_name.lower().strip())
        if normalized_name in self.__id_map:
            return self.__id_map[normalized_name]

        if normalized_name not in self.__name_map:
            logging.error("Could not find name '{}' in name map dict.".format(
                speaker_name))
            full_name = speaker_name
        else:
            full_name = self.__name_map[normalized_name]

        speaker_id = self.__build_speaker_id(full_name)
        self.__id_map[normalized_name] = speaker_id
        return speaker_id

    def get_speaker_name(self, full_name: str) -> str:
        """Get the speaker name.""" ""
        return full_name

    def __build_speaker_id(self, full_name: str) -> str:
        """Build the speaker id from full name.

        Parameters
        ----------
        full_name: str, required
            The full name of the speaker.

        Returns
        -------
        speaker_id: str
            The id of the speaker.
        """
        canonical_id = full_name.translate(self.__translations)
        canonical_id = re.sub(r"-{2,}", '-', canonical_id)
        return "#{}".format(canonical_id)
