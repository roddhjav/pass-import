# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

from xml.parsers.expat import ExpatError

try:
    from defusedxml import ElementTree
    from defusedxml.ElementTree import ParseError
    from defusedxml.minidom import parse
except ImportError:
    from xml.etree import ElementTree
    from xml.etree.ElementTree import ParseError
    from xml.dom.minidom import parse

from pass_import.core import Cap, register_detecters
from pass_import.detecter import Formatter
from pass_import.errors import FormatError
from pass_import.manager import PasswordImporter


class XML(Formatter, PasswordImporter):
    """Base class for XML based importers.

    :param dict xml_header: XML root tag and doctype.

    """
    cap = Cap.FORMAT | Cap.IMPORT
    format = 'xml'
    xml_header = {}
    tree = None
    dom = None

    # Import methods

    @classmethod
    def _getroot(cls, tree):
        return tree

    @classmethod
    def _getvalue(cls, element):
        return element.tag, element.text

    def _getentry(self, elements):
        entry = {}
        keys = self.invkeys()
        for element in elements:
            xmlkey, value = self._getvalue(element)
            key = keys.get(xmlkey, xmlkey)
            entry[key] = value
        return entry

    def _import(self, element, path=''):
        """Import method for XML based importer."""
        raise NotImplementedError()

    def parse(self):
        """Parse XML based file."""
        self.tree = ElementTree.XML(self.file.read())
        if not self.checkheader(self.header()):
            raise FormatError()
        root = self._getroot(self.tree)
        self._import(root)

    # Format recognition methods

    def is_format(self):
        """Return True if the file is an XML file."""
        try:
            self.dom = parse(self.file)
        except (ParseError, ExpatError, UnicodeDecodeError):
            return False
        return True

    def checkheader(self, header, only=False):
        """Ensure the file header is the same than the pm header."""
        if self.dom:
            if self.dom.doctype:
                if self.dom.doctype.toxml() != header.get('doctype', ''):
                    return False
            if self.dom.documentElement.tagName != header.get('root', ''):
                return False
        elif self.tree.tag != header.get('root', ''):
            return False
        return True

    @classmethod
    def header(cls):
        """Header for XML file."""
        return cls.xml_header


class HTML(Formatter, PasswordImporter):
    """Base class for HTML based importers."""
    cap = Cap.FORMAT | Cap.IMPORT
    format = 'html'
    html_header = ''
    tree = None

    # Import method

    def parse(self):
        """Parse HTML based file."""
        raise NotImplementedError()

    # Format recognition methods

    def is_format(self):
        """Return True if the file is an HTML file."""
        try:
            self.tree = ElementTree.XML(self.file.read())
            if self.tree.tag != 'html':
                return False
        except (ParseError, ExpatError):
            return False
        return True

    def checkheader(self, header, only=False):
        """Ensure the file header is the same than the pm header."""
        found = self.tree.find(header)
        if found is None:
            return False
        return True

    @classmethod
    def header(cls):
        """Header for HTML file."""
        return cls.html_header


register_detecters(XML, HTML)
