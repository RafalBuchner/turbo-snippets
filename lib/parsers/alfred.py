if __name__ == "__main__":
    from base import BaseParser
else:
    from .base import BaseParser
import json
import os
import uuid
import tempfile
import zipfile


class AlfredParser(BaseParser):
    implemented=True
    formatName = ''
    def saveJson(self, entry):
        filename = entry["alfredsnippet"]["name"] + " " + entry["alfredsnippet"]["uid"] + ".json"
        with open(filename, "w") as outfile:
            json.dump(entry, outfile)
        return outfile.name

    def genUuid(self):
        return str(uuid.uuid4())

    def getSnippets(self):
        alfredSnippets = []
        for entry in self.data:
            tempdict = dict()
            tempdict["snippet"] = entry['text'].replace('$','')
            tempdict["uid"] = self.genUuid()
            tempdict["name"] = entry.get('alfred_name', entry['abbreviation'])
            tempdict["keyword"] = entry['abbreviation']
            snippet = {"alfredsnippet": tempdict}
            alfredSnippets.append(snippet)
        return alfredSnippets


    def save(self):
        filename = self.path
        alfredEntries = self.getSnippets()
        with tempfile.TemporaryDirectory() as tmpDir:
            os.chdir(tmpDir)
            fileList = []
            for entry in alfredEntries:
                fileList.append(self.saveJson(entry))
            outputFilename = filename + ".alfredsnippets"
            with zipfile.ZipFile(outputFilename, "w", zipfile.ZIP_DEFLATED) as zf:
                for entry in fileList:
                    zf.write(entry)
                zf.close()
            os.rename(outputFilename, os.path.join(self.dir, outputFilename))

    def test(self):
        return AlfredParser.genUuid()



if __name__ == '__main__':
    data = [{'abbreviation': 'varname', 'description': "I'm doing something sossy", 'text': '$nana$ = $ula$()', 'variables': [{'name': 'nana', 'expression': '', 'default_value': '', 'skip_if_defined': ''}, {'name': 'ula', 'expression': '', 'default_value': '', 'skip_if_defined': ''}]}, {'abbreviation': 'blablabla',
                                                                                                                                                                                                                                                                                                'description': 'nothing so important', 'text': '$currentFont$ = CurrentFont()\n\nfor glyph in $currentFont$:\n    # $END$', 'variables': [{'name': 'currentFont', 'expression': '', 'default_value': '', 'skip_if_defined': ''}, {'name': 'END', 'expression': '', 'default_value': '', 'skip_if_defined': ''}]}]
    settings = dict(group_name='test', soft_tabs=True, spaces_in_tab=4)
    parser = AlfredParser(data, settings, os.getcwd())
    parser.save()
