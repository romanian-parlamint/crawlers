"""Module responsible for creating root XML files."""
from .namemapping import SpeakerInfoProvider
from .xmlstats import CorpusStatsWriter
from .xmlstats import SessionStatsReader
from .xmlutils import XmlDataManipulator
from .xmlutils import XmlElements, XmlAttributes
from datetime import date
from datetime import datetime
from lxml import etree
from typing import Generator
from typing import List
from typing import Tuple
import logging


class RootCorpusFileBuilder(XmlDataManipulator):
    """Builds the root file of the corpus."""

    def __init__(self, file_path: str, template_file: str,
                 speaker_info_provider: SpeakerInfoProvider):
        """Create a new instance of the class.

        Parameters
        ----------
        file_path: str, required
            The path of the corpus root file.
        template_file: str, required
            The path of the corpus root template file.
        speaker_info_provider: SpeakerInfoProvider, required
            An instance of SpeakerInfoProvider used for filling speaker info.
        """
        XmlDataManipulator.__init__(self, template_file)
        self.__file_path = file_path
        self.__speaker_info_provider = speaker_info_provider

    def add_corpus_file(self, corpus_file: str):
        """Add the specified file to the corpus root file.

        Parameters
        ----------
        corpus_file: str, required
            The path of the file to add to the corpus.
        """
        self.__update_tag_usage(corpus_file)
        self.__add_component_file(corpus_file)
        self.save_changes(self.__file_path)

    def __add_component_file(self, component_path: str):
        """Add the component path to the `include` element.

        Parameters
        ----------
        component_path: str, required
            The path of the corpus component file.
        """
        etree.register_namespace("xsi", "http://www.w3.org/2001/XInclude")
        qname = etree.QName("http://www.w3.org/2001/XInclude", "include")
        include_element = etree.Element(qname)
        include_element.set("href", component_path)
        self.xml_root.append(include_element)

    def __update_tag_usage(self, component_path: str):
        """Update the values of `tagUsage` element with the values from the corpus component file.

        Parameters
        ----------
        component_path: str, required
            The path of the corpus component file.
        """
        provider = SessionStatsReader(component_path)
        writer = CorpusStatsWriter(self.xml_root, provider)
        writer.update_statistics()
