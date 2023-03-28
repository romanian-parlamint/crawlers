"""Utilities for XML conversion."""
from lxml import etree


class XmlElements:
    """Names of the XML elements to build or parse."""

    TEI = '{http://www.tei-c.org/ns/1.0}TEI'
    titleStmt = '{http://www.tei-c.org/ns/1.0}titleStmt'
    title = '{http://www.tei-c.org/ns/1.0}title'
    meeting = '{http://www.tei-c.org/ns/1.0}meeting'
    u = '{http://www.tei-c.org/ns/1.0}u'
    div = '{http://www.tei-c.org/ns/1.0}div'
    extent = '{http://www.tei-c.org/ns/1.0}extent'
    measure = '{http://www.tei-c.org/ns/1.0}measure'
    date = '{http://www.tei-c.org/ns/1.0}date'
    bibl = '{http://www.tei-c.org/ns/1.0}bibl'
    setting = '{http://www.tei-c.org/ns/1.0}setting'
    tagUsage = '{http://www.tei-c.org/ns/1.0}tagUsage'
    text = '{http://www.tei-c.org/ns/1.0}text'
    body = '{http://www.tei-c.org/ns/1.0}body'
    head = '{http://www.tei-c.org/ns/1.0}head'
    note = '{http://www.tei-c.org/ns/1.0}note'
    seg = '{http://www.tei-c.org/ns/1.0}seg'
    kinesic = '{http://www.tei-c.org/ns/1.0}kinesic'
    desc = '{http://www.tei-c.org/ns/1.0}desc'
    gap = '{http://www.tei-c.org/ns/1.0}gap'
    idno = '{http://www.tei-c.org/ns/1.0}idno'
    listOrg = '{http://www.tei-c.org/ns/1.0}listOrg'
    org = '{http://www.tei-c.org/ns/1.0}org'
    orgName = '{http://www.tei-c.org/ns/1.0}orgName'
    event = '{http://www.tei-c.org/ns/1.0}event'
    listPerson = '{http://www.tei-c.org/ns/1.0}listPerson'
    person = '{http://www.tei-c.org/ns/1.0}person'
    persName = '{http://www.tei-c.org/ns/1.0}persName'
    forename = '{http://www.tei-c.org/ns/1.0}forename'
    surname = '{http://www.tei-c.org/ns/1.0}surname'
    sex = '{http://www.tei-c.org/ns/1.0}sex'
    affiliation = '{http://www.tei-c.org/ns/1.0}affiliation'
    figure = '{http://www.tei-c.org/ns/1.0}figure'
    graphic = '{http://www.tei-c.org/ns/1.0}graphic'
    s = '{http://www.tei-c.org/ns/1.0}s'
    w = '{http://www.tei-c.org/ns/1.0}w'
    pc = '{http://www.tei-c.org/ns/1.0}pc'
    linkGrp = '{http://www.tei-c.org/ns/1.0}linkGrp'
    link = '{http://www.tei-c.org/ns/1.0}link'


class XmlAttributes:
    """Constants used for names of XML attributes."""

    ana = 'ana'
    corresp = 'corresp'
    element_type = 'type'
    event_end = 'to'
    event_start = 'from'
    full = 'full'
    gi = 'gi'
    lang = '{http://www.w3.org/XML/1998/namespace}lang'
    lemma = 'lemma'
    meeting_n = 'n'
    msd = 'msd'
    occurs = 'occurs'
    pos = 'pos'
    quantity = 'quantity'
    ref = 'ref'
    role = 'role'
    role = 'role'
    targFunc = 'targFunc'
    target = 'target'
    type_ = 'type'
    unit = 'unit'
    url = 'url'
    value = 'value'
    when = 'when'
    who = 'who'
    xml_id = '{http://www.w3.org/XML/1998/namespace}id'


class Resources:
    """Resource strings."""

    SessionTitleRo = "Corpus parlamentar român ParlaMint-RO, ședința Camerei Deputaților din {}"
    SessionSubtitleRo = "Stenograma ședinței Camerei Deputaților din România din {}"
    SessionTitleEn = "Romanian parliamentary corpus ParlaMint-RO, Regular Session, Chamber of Deputies, {}"
    SessionSubtitleEn = "Minutes of the session of the Chamber of Deputies of Romania, {}"
    Heading = "ROMÂNIA CAMERA DEPUTAȚILOR"
    SessionHeading = "Ședinta Camerei Deputaților din {}"
    ToC = "SUMAR"
    NumSpeechesRo = "{} discursuri"
    NumSpeechesEn = "{} speeches"
    NumWordsRo = "{} cuvinte"
    NumWordsEn = "{} words"


def load_xml(file_name):
    """Load the specified XML file.

    Parameters
    ----------
    file_name: str, required
        The name of the XML file.

    Returns
    -------
    xml_tree: etree.ElementTree
        The XML tree from the file.
    """
    parser = etree.XMLParser(remove_blank_text=True)
    xml_tree = etree.parse(file_name, parser)
    return xml_tree


def save_xml(xml: etree._ElementTree, file_name: str):
    """Save the provided XML tree to the specified file.

    Parameters
    ----------
    xml : etree.ElementRoot, required
        The XML tree to save to disk.
    file_name : str, required
        The file where to save the XML.
    """
    xml.write(file_name,
              pretty_print=True,
              encoding='utf-8',
              xml_declaration=True)


class XmlDataManipulator:
    """Provide basic abstractions for manipulating a XML file."""

    def __init__(self, xml_file: str):
        """Create a new instance of the class.

        Parameters
        ----------
        xml_file: str, required
            The path of the XML file.
        """
        self.__xml_file = xml_file
        self.__xml_tree = load_xml(xml_file)

    @property
    def xml_root(self):
        """Get the root node of the XML tree."""
        return self.__xml_tree.getroot()

    def save_changes(self, output_file: str = None):
        """Save the changes made to the XML tree.

        Parameters
        ----------
        output_file: str, optional
            The file where to save the changes.
            If `None` then changes will be saved to the input file.
        """
        xml_file = output_file if output_file is not None else self.__xml_file
        save_xml(self.__xml_tree, xml_file)
