"""Module responsible for conversion from JSON to  XML."""
import logging
from pathlib import Path


class SessionTranscriptConverter:
    """Convert session transcript from JSON to XML."""

    def __init__(self, input_file: str, session_template: str,
                 output_dir: str):
        """Create a new instance of the class.

        Parameters
        ----------
        input_file: str, required
            The path of the session transcript in JSON format.
        session_template: str, required
            The path of the XML file containing session template.
        output_dir: Path, required
            The path of the output directory.
        """
        self.__input_file = input_file
        self.__output_file = self.__build_output_file_path(
            input_file, output_dir)

    def covert(self):
        """Convert session transcript to XML format."""
        logging.info("Converting from {} to {}.".format(
            self.__input_file, self.__output_file))

    def __build_output_file_path(self, input_file: str,
                                 output_dir: str) -> str:
        """Build the path of the output file.

        Parameters
        ----------
        input_file: str, required
            The path of the session transcript in JSON format.
        output_dir: Path, required
            The path of the output directory.

        Returns
        -------
        output_file: str
            The path of the output file.
        """
        output_dir = Path(output_dir)
        input_file = Path(input_file)
        file_path = Path('ParlaMint-RO-{}.xml'.format(input_file.stem))
        output_file = output_dir / file_path
        return str(output_file)
