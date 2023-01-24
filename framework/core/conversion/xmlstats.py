"""Module responsible for statistics counts in session transcripts and root corpus file."""
from typing import List
from typing import Dict
from typing import Callable
from lxml import etree
from .xmlutils import XmlDataManipulator
from .xmlutils import XmlAttributes
from .xmlutils import XmlElements
from .xmlutils import Resources


class SessionStatsCalculator(XmlDataManipulator):
    """Calculate the statistics for one session transcript."""

    def __init__(self, xml_file: str, word_tokenizer: Callable[[str],
                                                               List[str]]):
        """Create a new instance of the class.

        Parameters
        ----------
        xml_file: str, required
            The file containing session transcript in XML format.
        word_tokenizer: callback, required
            A callback function that accepts a string as input, tokenizes it and returns a list of tokens.
        """
        XmlDataManipulator.__init__(self, xml_file)
        self.__tokenizer = word_tokenizer

    def get_num_words(self) -> int:
        """Compute the number of words from the session transcription.

        Returns
        -------
        num_words: int
            The number of words in the transcription.
        """
        debate_section = None
        for div in self.xml_root.iterdescendants(XmlElements.div):
            if div.get(XmlAttributes.element_type) == "debateSection":
                debate_section = div
        text = "".join(debate_section.itertext())
        num_words = len(self.__tokenizer(text))
        return num_words

    def get_num_speeches(self) -> int:
        """Compute the number of utterances.

        Returns
        -------
        num_speeches: int
            The number of speeches in the transcription.
        """
        speeches = [
            s for s in self.xml_root.iterdescendants(tag=XmlElements.u)
        ]
        num_speeches = len(speeches)
        return num_speeches

    def get_tag_counts(self) -> Dict[str, int]:
        """Compute the number of times each tag appears in the document.

        Returns
        -------
        tag_counts: dict of (str, int)
            A dictionary containing each tag and the number of times it appears in the document.
        """
        tag_counts = {}
        for element in self.xml_root.iterdescendants():
            tag = str(element.tag)
            count = tag_counts[tag] if tag in tag_counts else 0
            tag_counts[tag] = count + 1
        return tag_counts


class SessionStatsWriter(XmlDataManipulator):
    """Update the values for tags containing session statistics."""

    def __init__(self, xml_file: str, stats_provider: SessionStatsCalculator):
        """Create a new instance of the class.

        Parameters
        ----------
        xml_file: str, required
            The path of the XML file for which to update the statistics.
        stats_provider: SessionStatsCalculator, required
            The object that provides the statistics values.
        """
        XmlDataManipulator.__init__(self, xml_file)
        self.__provider = stats_provider

    def update_statistics(self):
        """Update the tagUsage elements."""
        self.__set_session_stats()
        self.__set_tag_usage()
        self.save_changes()

    def __set_tag_usage(self):
        """Update the values for tagUsage elements."""
        tag_counts = self.__provider.get_tag_counts()
        name_map = {
            "text": XmlElements.text,
            "body": XmlElements.body,
            "div": XmlElements.div,
            "head": XmlElements.head,
            "note": XmlElements.note,
            "u": XmlElements.u,
            "seg": XmlElements.seg,
            "kinesic": XmlElements.kinesic,
            "desc": XmlElements.desc,
            "gap": XmlElements.gap
        }
        for tag_usage in self.xml_root.iterdescendants(
                tag=XmlElements.tagUsage):
            tag_name = name_map[tag_usage.get(XmlAttributes.gi)]
            num_occurences = tag_counts[
                tag_name] if tag_name in tag_counts else 0
            tag_usage.set(XmlAttributes.occurs, str(num_occurences))

    def __set_session_stats(self):
        """Set the values of the session statistics elements."""
        num_speeches = self.__provider.get_num_speeches()
        num_words = self.__provider.get_num_words()
        for m in self.xml_root.iterdescendants(tag=XmlElements.measure):
            if m.getparent().tag != XmlElements.extent:
                continue
            lang = m.get(XmlAttributes.lang)
            unit = m.get(XmlAttributes.unit)

            qty = num_speeches if unit == 'speeches' else num_words
            m.set(XmlAttributes.quantity, str(qty))
            if unit == 'speeches':
                txt = Resources.NumSpeechesRo if lang == 'ro' else Resources.NumSpeechesEn
            else:
                txt = Resources.NumWordsRo if lang == 'ro' else Resources.NumWordsEn
            m.text = txt.format(qty)


class SessionStatsReader(XmlDataManipulator):
    """Reads the statistics from session XML file."""

    def __init__(self, xml_file: str):
        """Create a new instance of the class.

        Parameters
        ----------
        xml_file: str, required
            The path of the session XML file from where to read stats.
        """
        XmlDataManipulator.__init__(self, xml_file)

    def get_num_words(self) -> int:
        """Compute the number of words from the session transcription.

        Returns
        -------
        num_words: int
            The number of words in the transcription.
        """
        return self.__get_measure('words')

    def get_num_speeches(self) -> int:
        """Compute the number of utterances.

        Returns
        -------
        num_speeches: int
            The number of speeches in the transcription.
        """
        return self.__get_measure('speeches')

    def get_tag_counts(self) -> Dict[str, int]:
        """Compute the number of times each tag appears in the document.

        Returns
        -------
        tag_counts: dict of (str, int)
            A dictionary containing each tag and the number of times it appears in the document.
        """
        tag_counts = {}
        for tag_usage in self.xml_root.iterdescendants(
                tag=XmlElements.tagUsage):
            tag_type = tag_usage.get(XmlAttributes.gi)
            num_occurences = int(tag_usage.get(XmlAttributes.occurs))
            tag_counts[tag_type] = num_occurences
        return tag_counts

    def __get_measure(self, unit: str, lang: str = "ro") -> int:
        """Get the value of a measure element with the specified unit and language.

        Parameters
        ----------
        unit: str, required
            The unit of the element.
        lang: str, required
            The language of the element.

        Returns
        -------
        quantity: int
            The value of the measure.
        """
        for m in self.xml_root.iterdescendants(tag=XmlElements.measure):
            if m.getparent().tag != XmlElements.extent:
                continue
            measure_unit = m.get(XmlAttributes.unit)
            measure_lang = m.get(XmlAttributes.lang)
            if measure_unit == unit and measure_lang == lang:
                return int(m.get(XmlAttributes.quantity))
        return None


class CorpusStatsWriter:
    """Updates the statistics for the root corpus file."""

    def __init__(self, xml_root: etree.Element,
                 stats_provider: SessionStatsReader):
        """Create a new instance of the class.

        Parameters
        ----------
        xml_root: etree.Element, required
            The root element of the corpus file.
        stats_provider: SessionStatsReader, required
            The provider of the session statistics.
        """
        self.__xml_root = xml_root
        self.__provider = stats_provider

    def update_statistics(self):
        """Update the corpus statistics with the values from the statistics provider."""
        self.__update_speech_counts()
        self.__update_tag_usage()

    def __update_speech_counts(self):
        """Update the counts for number of speeches and number of words."""
        num_speeches = self.__provider.get_num_speeches()
        num_words = self.__provider.get_num_words()
        for m in self.__xml_root.iterdescendants(tag=XmlElements.measure):
            if m.getparent().tag != XmlElements.extent:
                continue
            lang = m.get(XmlAttributes.lang)
            unit = m.get(XmlAttributes.unit)
            quantity = int(m.get(XmlAttributes.quantity))

            delta = num_speeches if unit == 'speeches' else num_words
            quantity += delta

            m.set(XmlAttributes.quantity, str(quantity))
            if unit == 'speeches':
                txt = Resources.NumSpeechesRo if lang == 'ro' else Resources.NumSpeechesEn
            else:
                txt = Resources.NumWordsRo if lang == 'ro' else Resources.NumWordsEn
            m.text = txt.format(quantity)

    def __update_tag_usage(self):
        """Update the counts for tag usage."""
        tag_counts = self.__provider.get_tag_counts()
        for tag_usage in self.__xml_root.iterdescendants(
                tag=XmlElements.tagUsage):
            tag_name = tag_usage.get(XmlAttributes.gi)
            num_occurences = int(tag_usage.get(XmlAttributes.occurs))
            delta = tag_counts[tag_name] if tag_name in tag_counts else 0
            num_occurences += delta
            tag_usage.set(XmlAttributes.occurs, str(num_occurences))
