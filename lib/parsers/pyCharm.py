if __name__=="__main__":
    from base import BaseParser
else:
    from .base import BaseParser
import xml.etree.ElementTree as ET
import os
translate = {
    # "\"": "&quote;",
    # "<": "&lt;",
    # "\n": '&#10;',
    # ">": "&gt;",
    # # "&": "&amp;",
    # "~": "&tilde;",
}


class PyCharmParser(BaseParser):
    implemented=True
    formatName = 'xml'
    wrappers = {
        'left_var': None,
        'right_var': None,
        'left_snippet': None,
        'right_snippet': None,
        'key_abbreviation': 'name',
        'key_description': None,
        'key_text': 'value',
        'key_sourceCode': 'Python',
        False: 'false',
        True: 'true',
    }

    def __init__(self, data, settings, path):
        super(PyCharmParser, self).__init__(data=data, settings=settings, path=path)
        self.softTabs = True
        self.spacesInTab = 4

    def save(self):
        basename = os.path.basename(self.path)
        dirName = os.path.dirname(self.path)
        path = os.path.join(dirName,basename.title())
        
        with open(path, 'wb') as f:
            f.write(self.getData())

    def _constructXML(self):
        templeSet = self.xml.Element("templateSet", group=self.groupName)
        snippets = []
        for snippet in self.data:
            value = snippet['text']
            template = self.xml.Element('template', name=snippet['abbreviation'], 
                description=snippet['description'], value=value, toReformat=self.wrappers[False],toShortenFQNames=self.wrappers[True])

            variables = []

            for varData in snippet['variables']:
                name = varData.get('name')
                expression = varData.get('expression')
                defaultValue = varData.get('default_value')

                if varData.get('skip_if_defined') is not None:
                    if varData.get('skip_if_defined') == 1:
                        alwaysStopAt = self.wrappers[False]
                    else:
                        alwaysStopAt = self.wrappers[True]

                variable = self.xml.Element('variable',
                                            name=name,
                                            expression=expression,
                                            defaultValue=defaultValue,
                                            alwaysStopAt=alwaysStopAt,

                                            )
                for attrName in variable.attrib.keys():
                    if variable.attrib[attrName] == "":
                        del variable.attrib[attrName]
                template.insert(-1, variable)

            option = self.xml.Element('option', name=self.wrappers[
                                       'key_sourceCode'], value=self.wrappers[True])
            context = self.xml.Element('context')
            context.insert(0, option)
            template.insert(-0, context)

            templeSet.insert(-1, template)

        self._txt = self.xml.tostring(templeSet, pretty_print=True)

if __name__ == '__main__':

    from pprint import pprint
    data = [{'abbreviation': 'varname', 'description': "I'm doing something sossy", 'text': '$nana$ = $ula$()', 'variables': [{'name': 'nana', 'expression': '', 'default_value': '', 'skip_if_defined': ''}, {'name': 'ula', 'expression': '', 'default_value': '', 'skip_if_defined': ''}]}, {'abbreviation': 'blablabla',
                                                                                                                                                                                                                                                                                                'description': 'nothing so important', 'text': '$currentFont$ = CurrentFont()\n\nfor glyph in $currentFont$:\n    # $END$', 'variables': [{'name': 'currentFont', 'expression': '', 'default_value': '', 'skip_if_defined': ''}, {'name': 'END', 'expression': '', 'default_value': '', 'skip_if_defined': ''}]}]

    settings = dict(group_name='test', soft_tabs=True, spaces_in_tab=4)
    test = PyCharmParser(data, settings, os.getcwd())
    test.save()
