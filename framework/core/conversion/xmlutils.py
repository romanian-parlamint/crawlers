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

    xml_id = '{http://www.w3.org/XML/1998/namespace}id'
    lang = '{http://www.w3.org/XML/1998/namespace}lang'
    element_type = 'type'
    meeting_n = 'n'
    unit = 'unit'
    quantity = 'quantity'
    when = 'when'
    gi = 'gi'
    occurs = 'occurs'
    ana = 'ana'
    who = 'who'
    full = 'full'
    role = 'role'
    event_start = 'from'
    event_end = 'to'
    value = 'value'
    url = 'url'
    ref = 'ref'
    role = 'role'
    msd = 'msd'
    pos = 'pos'
    lemma = 'lemma'
    targFunc = 'targFunc'
    type_ = 'type'
    target = 'target'
    corresp = 'corresp'


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
    for element in xml_tree.iter():
        element.tail = None
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
