import lxml.etree
import os
# import lxml.builder


class BaseParser(object):
    formatName = 'xml'
    wrappers = dict(
        left_var=None,
        right_var=None,
        left_snippet=None,
        right_snippet=None,
        key_abbreviation=None,
        key_description=None,
        key_text=None,
        key_sourceCode=None,
    )

    def __init__(self, data, settings, path=''):
        self._txt = b''
        self.softTabs = settings['soft_tabs']
        self.groupName = settings['group_name']
        self.path = os.path.join(path, self.groupName + "." + self.formatName)
        if len(self.formatName) == 0:
            print(self.groupName)
            self.path = os.path.join(path, self.groupName)
        self.dir = os.path.dirname(self.path)
        self.spacesInTab = settings.get('spaces_in_tab')
        self.data = data
        self.xml = lxml.etree
        self._constructXML()

    def _constructXML(self):
        self._txt = None

    def save(self):
        with open(self.path, 'wb') as f:
            f.write(self.getData())

    def getData(self):
        return self._txt

if __name__ == '__main__':
    bp = BaseParser(None, None)
    bp.getData()
