# -*- coding: utf-8 -*-
if __name__=="__main__":
    from base import BaseParser
else:
    from .base import BaseParser
# import xml.etree.ElementTree as ET
import xml.etree.ElementTree as ET
import xml.etree
# import lxml.html
import re
import os
import cgi
import html


class SublimeParser(BaseParser):
    implemented=True
    formatName = 'sublime-snippet'
    wrappers = {
        'left_var': '${num:',
        'right_var': '}',
        'left_snippet': '<![CDATA[',
        'right_snippet': ']]>',
        'key_abbreviation': 'tabTrigger',
        'key_description': 'description',
        'key_text': 'content',
        'key_sourceCode': 'source',
        False: True,
        True: False,
    }
    def __init__(self, data, settings, path):
        self.snippets = {}
        super(SublimeParser, self).__init__(data=data, settings=settings,path=path)
        self.softTabs = True
        self.spacesInTab = 4
        self.xml = xml.etree

    def getData(self):
        return html.unescape(self._txt.decode('utf-8'))

    def save(self):
        basename = os.path.basename(self.path)
        dirName = os.path.dirname(self.path)
        boundleDir = os.path.join(dirName, self.groupName)
        if not os.path.exists(boundleDir):
            os.mkdir(boundleDir)
        path = os.path.join(dirName, self.groupName)
        for snippetName in self.snippets:
            data = html.unescape(self.snippets[snippetName].decode('utf-8'))
            snippetPath = os.path.join(path,snippetName + "." + self.formatName)
            with open(snippetPath, 'w') as f:
                f.write(data)

    def _constructXML(self):

        self._txt = b''
        for snippet in self.data:
            text = snippet['text']
            sourceTxt = snippet.get('source', None)
            for i, var in enumerate(snippet['variables']):
                order = var.get('order', str(i+1))
                if not order.isdigit(): order = str(i)

                name = var['name']
                newName = self.wrappers['left_var'].replace('num', str(order)) + name + self.wrappers['right_var']
                text = text.replace('$'+name+'$', newName)

            snippetEntry = self.xml.Element("snippet")
            tabTrigger = self.xml.Element("tabTrigger")
            content = self.xml.Element("content")
            description = self.xml.Element("description")
            scope = self.xml.Element("scope")
            content.text = self.wrappers['left_snippet'] + text + self.wrappers['right_snippet']
            description.text = snippet.get('description')
            scope.text = sourceTxt

            tabTrigger.text = snippet.get('abbreviation')
            if sourceTxt is None:
                # TEMP
                scope.text = 'source.python'

            if sourceTxt is not None:
                snippetEntry.insert(-1, scope)
            snippetEntry.insert(-1, content)
            snippetEntry.insert(-1, tabTrigger)
            if snippet.get('description') is not None:
                snippetEntry.insert(-1, description)
            self.snippets[tabTrigger.text] = self.xml.tostring(snippetEntry, pretty_print=True)
            self._txt += self.xml.tostring(snippetEntry, pretty_print=True,xml_declaration=False,exclusive=True)



if __name__ == '__main__':
    from pprint import pprint
    data = [{'abbreviation': 'varname', 'description': "I'm doing something sossy", 'text': '$nana$ = $ula$()', 'variables': [{'name': 'nana', 'expression': '', 'default_value': '', 'skip_if_defined': ''}, {'name': 'ula', 'expression': '', 'default_value': '', 'skip_if_defined': ''}]}, {'abbreviation': 'blablabla',
                                                                                                                                                                                                                                                                                                'description': 'nothing so important', 'text': '$currentFont$ = CurrentFont()\n\nfor glyph in $currentFont$:\n    # $END$', 'variables': [{'name': 'currentFont', 'expression': '', 'default_value': '', 'skip_if_defined': ''}, {'name': 'END', 'expression': '', 'default_value': '', 'skip_if_defined': ''}]}]
    settings = dict(group_name='test', soft_tabs=True, spaces_in_tab=4)
    test = SublimeParser(data, settings, os.getcwd())
    test.save()
