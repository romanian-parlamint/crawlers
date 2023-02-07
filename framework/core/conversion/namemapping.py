"""Module responsible for mapping speaker names to their information."""
import logging
import re
from typing import Dict
from typing import List
from unidecode import unidecode


class SpeakerInfo:
    """Represents information about the speaker."""

    def __init__(self,
                 first_name: List[str],
                 last_name: List[str],
                 speaker_id: str = None,
                 sex: str = "U",
                 profile_image: str = None):
        """Create a new instance of the class.

        Parameters
        ----------
        first_name: list of str, required
            The parts of the first name.
        last_name: list of str, required
            The parts of the last name.
        speaker_id: str, optional
            The id of the speaker.
        sex: str, optional
            The sex of the speaker. Default value is U which means unknown.
        profile_image: str, optional
            The URL of the profile image.
        """
        self.__translations = str.maketrans({'Ş': 'Ș', 'ş': 'ș'})
        self.__first_name = self.__translate_name(first_name)
        self.__last_name = self.__translate_name(last_name)
        self.__speaker_id = None
        self.__sex = 'U'
        self.__profile_image = None
        # Set the properties
        self.speaker_id = speaker_id
        self.sex = sex
        self.profile_image = profile_image

    @property
    def profile_image(self) -> str:
        """Get the profile image URL.

        Returns
        -------
        profile_image: str
            The URL of the profile image.
        """
        return self.__profile_image

    @profile_image.setter
    def profile_image(self, value: str):
        """Set the profile image.

        Parameters
        ----------
        value: str, required
            The URL of the profile image.
        """
        self.__profile_image = value

    @property
    def sex(self) -> str:
        """Get the sex of the speaker.

        Returns
        -------
        sex: one of [M, F, U]
            The sex of the speaker: M(ale), F(emale), or U(nknown).
        """
        return self.__sex

    @sex.setter
    def sex(self, value: str):
        """Set the sex of the speaker.

        Parameters
        ----------
        value: str, one of [M, F, U], required
            The sex of the speaker.
        """ ""
        if value not in ['M', 'F', 'U']:
            raise ValueError("Sex must be one of 'M','F', or 'U'.")
        self.__sex = value

    @property
    def speaker_id(self) -> str:
        """Get the speaker id.

        Returns
        -------
        speaker_id: str
            The id of the speaker.
        """
        return self.__speaker_id

    @speaker_id.setter
    def speaker_id(self, value: str):
        """Set the speaker id.

        Parameters
        ----------
        value: str, required
            The speaker id.
        """
        self.__speaker_id = value

    @property
    def last_name(self) -> List[str]:
        """Get the last name.

        Returns
        -------
        last_name: list of str
            The parts of last name.
        """
        return self.__last_name

    @property
    def first_name(self) -> List[str]:
        """Get the first name.

        Returns
        -------
        first_name: list of str
            The parts of first name.
        """
        return self.__first_name

    def __translate_name(self, name: List[str]) -> List[str]:
        """Replace invalid characters in name.

        Parameters
        ----------
        name: list of str, required
            The name to translate.

        Returns
        -------
        translated_name: list of str
            The name with translated characters.
        """ ""
        return [p.translate(self.__translations) for p in name]


class SpeakerInfoProvider:
    """Provides speaker info."""

    EMPTY_SPEAKER = SpeakerInfo(['Necunoscut'], ['Necunoscut'],
                                speaker_id="Necunoscut-Necunoscut")

    def __init__(self, name_map: Dict[str, str],
                 personal_info: List[SpeakerInfo]):
        """Create a new instance of the class.

        Parameters
        ----------
        name_map: dict of (str, str), required
            The dictionary mapping names as they appear in JSON transcriptions to the correct names of speakers.
        personal_info: list of SpeakerInfo, required
            The list with personal info of the speakers.
        """
        self.__name_map = {self.__normalize(k): v for k, v in name_map.items()}
        self.__personal_info = {
            # Both first and last names are collections of multiple names
            self.__build_personal_info_key(*item.first_name + item.last_name):
            item
            for item in personal_info
        }
        self.__id_map = {}
        self.__info_map = {}
        self.__id_translations = str.maketrans({' ': '-'})

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
        normalized_name = self.__normalize(speaker_name)
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
        self.__info_map[speaker_id] = self.__get_personal_info(full_name)
        return speaker_id

    def get_personal_info(self, speaker_id: str) -> dict:
        """Get the personal info of the person with the specified id.

        Parameters
        ----------
        speaker_id: str, required
            The id of the speaker.

        Returns
        -------
        personal_info: dict
            The personal info.
        """ ""
        if not speaker_id.startswith('#'):
            speaker_id = '#' + speaker_id
        return self.__info_map[speaker_id]

    def get_speaker_name(self, full_name: str) -> str:
        """Get the speaker name.

        Parameters
        ----------
        full_name: str, required
            The full name of the speaker as it appears in the transcription.

        Returns
        -------
        speaker_name: str
            The name of the speaker.
        """
        normalized_name = self.__normalize(full_name)
        if normalized_name in self.__id_map:
            return self.__name_map[normalized_name]
        return full_name

    def __get_personal_info(self, full_name: str) -> dict:
        """Get the personal info of the person with the specified name.

        Parameters
        ----------
        full_name: str, required
            The full name of the person.

        Returns
        -------
        personal_data: dict
            The personal data.
        """
        key = self.__build_personal_info_key(full_name)

        if key in self.__personal_info:
            return self.__personal_info[key]

        logging.error("Could not find personal info for name '%s'.", full_name)
        info = EMPTY_SPEAKER
        self.__personal_info[key] = info
        return info

    def __build_personal_info_key(self, *full_name: str | List[str]) -> str:
        """Build the lookup key for personal info map.

        Parameters
        ----------
        full_name: str or list of str, required
            The full name of the person.

        Returns
        -------
        lookup_key: str
            The lookup key built from person name.
        """
        name = ' '.join(full_name)
        name = unidecode(name)
        parts = re.split(" |-", name)
        lookup_key = '#'.join(set([p.lower() for p in parts]))
        return lookup_key

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
        canonical_id = full_name.translate(self.__id_translations)
        canonical_id = re.sub(r"-{2,}", '-', canonical_id)
        return "#{}".format(unidecode(canonical_id))

    def __normalize(self, name: str) -> str:
        """Get the nomalized form of the specified name.

        Parameters
        ----------
        name: str, required
            The name to normalize.

        Returns
        -------
        canonical_name: str
            The normalized name.
        """
        return unidecode(name.lower().strip())
