#!/usr/bin/env python
"""Utility functions for session processing."""
import logging
import json
from pathlib import Path


def load_speakers(sessions_directory):
    """Parse sessions in the specified directory and load all speakers.

    Parameters
    ----------
    sessions_directory: str, required
        The directory containing the JSON files with session transcripts.

    Returns
    -------
    speakers: list of dict
        The list of all speakers from all sessions.
    """
    speakers = []
    for f in Path(sessions_directory).glob("*.json"):
        logging.info("Reading speakers from %s.", f)
        with open(str(f), 'r', encoding='utf8') as input_file:
            session = json.load(input_file)
            if 'sections' not in session:
                logging.error("Could not find session sections in %s.", f)
                continue

            for section in session['sections']:
                speaker = section['speaker']
                contents = section['contents']
                if contents is None or len(contents) == 0:
                    continue
                if speaker is None:
                    logging.warning("Found null speaker in section %s.",
                                    section)
                    continue

                speakers.append(speaker)

    return speakers
