# from drawBot.ui.codeEditor import *
from pyCodeEditor import CodeEditor
from vanilla import *
from collections import OrderedDict
from vanilla.dialogs import getFile, putFile, getFolder
from defcon.tools.notifications import NotificationCenter
from defconAppKit.windows.baseWindow import BaseWindowController
from misc import importSettings, exportSettings, findVariables, renameVariables, fileFormat, importFromTurboSnippets, exportToTurboSnippets
from parsers import *
from pprint import pprint
import os
homedir = os.getenv("HOME")
editorNameParser = OrderedDict([

    ('PyCharm', PyCharmParser),
    ('SublimeText', SublimeParser),
    ('Atom', AtomParser),
    ('Alfred', AlfredParser), 
    ]
)

defaultPaths = dict(
    PyCharm=os.path.join(homedir, '/Library/Preferences/PyCharmCE2019.1/templates'),
    SublimeText=os.path.join(homedir, '/Library/Application Support/Sublime Text 3/Packages/User'),
    Atom=os.path.join(homedir, '/.atom/'),
    # BBEdit=os.path.join(homedir),
    Alfred=os.path.join(homedir),
)
debug = True

fileFormat = 'turboSnippets'
center = NotificationCenter()
globalsettings = importSettings()

if globalsettings is None:
    globalsettings = {}
print(globalsettings)


class TurboSnippets(BaseWindowController):

    txtH = 17
    btnH = 22
    p = 10
    width = 700

    def __init__(self):


        self.firstOpen = True
        self.varList = []
        self.snippets = []

        x, y, p = [self.p] * 3
        view = Group((0, 0, -0, -0))
        view.generateBtn = SquareButton((x, y, self.width / 2 - p / 2 - x, self.btnH),
                                        'generate', callback=self.generateCallback)
        view.settingsBtn = SquareButton((x + self.width / 2 - p / 2, y, -p, self.btnH),
                                        'settings', callback=self.settingsCallback)
        y += self.btnH + p
        view.snippetGroupNameTitle = TextBox((x, y, 140, self.txtH), 'snippet group name')
        view.snippetGroupNameTxt = EditText(
            (x + 140 + p, y, 150, self.txtH), text='Untitled', sizeStyle='small', callback=self.editItemsCallback)
        view.snippetGroupNameTxt.title = 'snippetGroupName'
        y += self.btnH + p

        view.importBtn = SquareButton((x, y, self.width / 2 - p / 2 - x, self.btnH),
                                      'import', callback=self.importExportCallback)
        view.exportBtn = SquareButton((x + self.width / 2 - p / 2, y, self.width / 2 - p / 2 - x, self.btnH),
                                      'export', callback=self.importExportCallback)
        y += self.btnH + p
        listHeight = self.txtH * 10 + p
        columnDescriptions = [
            dict(title='abbreviation', editable=True),
            dict(title='description', editable=True),
            dict(title='alfred_name', editable=True),
        ]
        view.list = List((x, y, -p, listHeight), [],
                         columnDescriptions=columnDescriptions,
                         selectionCallback=self.snippetListNameSelectionCallback,
                         editCallback=self.snippetListNameEditCallback,
                         allowsEmptySelection=False)
        y += listHeight + p

        view.addBtn = SquareButton((x, y, self.btnH, self.btnH),
                                   '+', callback=self.addRemoveCallback)
        view.removeBtn = SquareButton((x + self.btnH + p, y, self.btnH, self.btnH),
                                      '-', callback=self.addRemoveCallback)
        y += self.btnH + p
        view.abbreviationTitle = TextBox((x, y, 85, self.txtH), 'abbreviation')
        view.abbreviationTxt = EditText(
            (x + 80 + p, y, 110, self.txtH), sizeStyle='small', callback=self.editItemsCallback)
        view.abbreviationTxt.title = 'abbreviation'
        view.descriptionTitle = TextBox(
            (x + 150 + 55, y, 85, self.txtH), 'description')
        view.descriptionTxt = EditText(
            (x + 150 + 55 + 70 + p, y, 208, self.txtH), sizeStyle='small', callback=self.editItemsCallback)
        view.descriptionTxt.title = 'description'
        view.alfred_nameTitle = TextBox(
            (x + 500, y, 85, self.txtH), 'alfred_name')
        view.alfred_nameTxt = EditText(
            (x + 500 + 75 + p, y, -p, self.txtH), sizeStyle='small', callback=self.editItemsCallback)
        view.alfred_nameTxt.title = 'alfred_name'
        y += self.btnH + p

        view.editVariablesBtn = SquareButton((x, y, -p, self.btnH),
                                             'edit variables', callback=self.editVariablesCallback)
        y += self.btnH + p

        self.codeEditorHeight = self.txtH * 20
        view.codeEditor = CodeEditor(
            (x, y, -p, self.codeEditorHeight), callback=self.codeEditCallback)

        self.height = y
        self.w = Window((self.width, self.height),
                        'TurboSnippets')  # , minSize=(100, 100))
        self.w.view = view
        self.w.open()
        self.w.view.codeEditor.show(False)
        center.addObserver(self, 'varListUpdatedEvent',
                           'varListUpdated')

    def setImportedTurboSnippets(self, turboSnippets):
        self.snippets = turboSnippets
        mainList = []
        snippetGroupName = ''

        for snippet in self.snippets:
            if isinstance(snippet, str):
                snippetGroupName = snippet

                continue
            
            # setting the main list
            print(1)
            abbreviation = snippet.get('abbreviation')
            description = snippet.get('description')
            alfred_name = snippet.get('alfred_name')
            print(2)
            mainList += [dict(abbreviation=abbreviation,
                              description=description, alfred_name=alfred_name)]

            # setting the variable list

            self.varList = list(snippet['variables'])
            self._varNames = [item['name'] for item in self.varList]
            self.updateVarItems()

        self.snippets.remove(snippetGroupName)
        self.w.view.list.set(mainList)
        if len(self.w.view.list) > 0:
            self.w.view.list.setSelection([0])
        self.snippetGroupName = snippetGroupName
        self.w.view.snippetGroupNameTxt.set(snippetGroupName)

    def varListUpdatedEvent(self, data):
        text = self.w.view.codeEditor.get()
        newVarNames = [item['name'] for item in data.data]
        if hasattr(self, '_varNames'):
            text = renameVariables(text, self._varNames, newVarNames)
            self.w.view.codeEditor.set(text)
            self._varNames = newVarNames
            self.varList = data.data
            self.updateVarItems()

    def snippetListNameSelectionCallback(self, sender):
        if sender.getSelection():
            items = sender.get()
            rowIndex = sender.getSelection()[0]
            item = items[rowIndex]
            snippet = self.snippets[rowIndex]
            abbreviation = item.get('abbreviation')
            description = item.get('description')
            snippet['abbreviation'] = abbreviation
            snippet['description'] = description
            self.w.view.abbreviationTxt.set(abbreviation)
            self.w.view.descriptionTxt.set(description)
            self.w.view.codeEditor.set(snippet['text'])

    def snippetListNameEditCallback(self, sender):
        items = sender.get()
        if len(items) > 0 and self.firstOpen:
            x, y, w, h = self.w.getPosSize()
            h += self.codeEditorHeight + self.p
            self.w.setPosSize((x, y, w, h))
            self.w.view.codeEditor.show(True)
            sender.setSelection([0])
            self.firstOpen = False

        if sender.getSelection():
            rowIndex = sender.getSelection()[0]
            item = items[rowIndex]
            snippet = self.snippets[rowIndex]
            abbreviation = item.get('abbreviation')
            description = item.get('description')
            alfred_name = item.get('alfred_name')
            snippet['abbreviation'] = abbreviation
            snippet['description'] = description
            snippet['alfred_name'] = description
            self.w.view.abbreviationTxt.set(abbreviation)
            self.w.view.descriptionTxt.set(description)
            self.w.view.alfred_nameTxt.set(alfred_name)
            self.w.view.codeEditor.set(snippet['text'])

    def editItemsCallback(self, sender):
        if sender.title == 'snippetGroupName':
            self.snippetGroupName = sender.get()
            # self.snippets += [dict(snippetGroupName=sender.get())]

        else:
            items = self.w.view.list.get()
            rowIndex = self.w.view.list.getSelection()[0]
            snippet = self.snippets[rowIndex]
            item = items[rowIndex]
            item[sender.title] = sender.get()
            snippet[sender.title] = sender.get()

    def codeEditCallback(self, sender):
        items = self.w.view.list.get()
        if self.w.view.list.getSelection():
            rowIndex = self.w.view.list.getSelection()[0]
            snippet = self.snippets[rowIndex]
            text = sender.get()
            self._varNames = findVariables(text)
            self.updateVarItems()
            snippet['text'] = text
            snippet['variables'] = self.varList

    def editVariablesCallback(self, sender):
        varSheet = VariableSheet(self.w)
        self.updateVarItems()
        varSheet.setVarList(self.varList)
        varSheet.open()

    def generateCallback(self, sender):
        print(globalsettings)
        generate = globalsettings.get('generate')
        print(2)
        settings = dict(
                spaces_in_tab=4,
                soft_tabs=True,
                group_name=self.snippetGroupName
            )
        print(3)
        if list(generate.keys()):
            print(2)
            for editorName in generate:
                print(333)
                if generate[editorName]:
                    print(444)
                    paths = globalsettings.get('paths')
                    print(444)
                    print(555)
                    if paths is None:
                        print(66)
                        paths = defaultPaths
                    path = paths[editorName]
                    if editorNameParser[editorName].implemented:
                        parser = editorNameParser[editorName](self.snippets, settings, path)
                        parser.save()

    def settingsCallback(self, sender):
        SettingsSheet(self.w)

    def importExportCallback(self, sender):
        def _exportCallback(path):
            data = [self.snippetGroupName] + self.snippets
            exportToTurboSnippets(path, data)

        def _importCallback(path):
            path = path[0]
            turboSnippets = importFromTurboSnippets(path)
            self.setImportedTurboSnippets(turboSnippets)

        if sender.getTitle() == 'export':
            self.showPutFile([fileFormat], _exportCallback)
            pass
        else:
            self.showGetFile([fileFormat], _importCallback)
            pass

    def addRemoveCallback(self, sender):
        items = self.w.view.list.get()
        if sender.getTitle() == '+':
            items += [dict(abbreviation=f"name/shortcut", description="description", alfred_name="name/shortcut in alfred")]

            self.snippets += [dict(
                abbreviation=f"name/shortcut",
                description="description",
                alfred_name="name/shortcut in alfred",
                text="# code here",
                variables=[]
            )]
            self.w.view.list.set(items)

        else:
            selection = self.w.view.list.getSelection()
            newItems = self.w.view.list.get()
            if items:
                for i in selection:
                    for item in items:
                        if newItems[i] == item:
                            del newItems[i]
                            break
                snippets = self.snippets
                for item in newItems:
                    for i, snippet in enumerate(self.snippets):
                        if item['abbreviation'] == snippet['abbreviation']:
                            del snippets[i]
                self.snippets = snippets

                self.w.view.list.set(newItems)

    def updateVarItems(self):
        varList = []
        if hasattr(self, '_varNames'):
            if self._varNames is not None:
                existingNamesInList = []
                for varItem in self.varList:
                    if varItem['name'] not in self._varNames:
                        continue
                    else:
                        varList += [varItem]
                        existingNamesInList += [varItem['name']]

                for varName in self._varNames:
                    if varName in existingNamesInList:
                        continue
                    newItem = [dict(name=varName, expression='',
                                    default_value='', skip_if_defined='')]
                    varList += newItem

        self.varList = varList


class SettingsSheet:

    def __init__(self, parentWindow):
        self.paths = globalsettings.get('paths', {})
        self.pathsHeight = 0
        x, self.y, p = [TurboSnippets.p] * 3
        self.txtH = TurboSnippets.txtH
        self.btnH = TurboSnippets.btnH
        view = Group((0, 0, -0, -0))
        path = '/parsers/'
        index = 0
        for editorName in editorNameParser:
            parser = editorNameParser[editorName]
            if hasattr(parser, 'implemented'):
                if parser.implemented:
                    self._createItem(view, editorName, index)
                    index += 1
        height = self.pathsHeight + p
        self.w = Sheet((600, height), parentWindow)
        self.w.view = view
        self.w.view.closeBtn = SquareButton(
            (0, -self.btnH, -0, self.btnH), "close", callback=self.closeSheet)
        self.w.view.settingsBtn = SquareButton(
            (0, -self.btnH * 2, -0, self.btnH), "apply", callback=self.settingsBtnCallback)
        self.w.open()
        self.parentWindow = parentWindow

    def _createItem(self, parentView, editorName, index):
        checkboxValues = globalsettings.get('generate')
        if checkboxValues:
            checkboxValue = checkboxValues.get(editorName, True)
        else:
            checkboxValue = True

        x, p = TurboSnippets.p, TurboSnippets.p
        path = self.paths.get(editorName, defaultPaths[editorName])
        # if index != 0:
        y = (index * self.btnH + p)
        # else: y = (self.btnH + p*2)

        view = Group((0, y, -0, self.btnH + p))
        view.editorNameBtn = SquareButton(
            (x, 0, 100, self.btnH), editorName, callback=self.getSavingPath)
        view.path = EditText((x + 100 + p, 2, -p - self.btnH, self.btnH), path, readOnly=True)
        view.checkbox = CheckBox((-self.btnH - 2, 2, self.btnH, self.btnH), "", value=checkboxValue)
        setattr(parentView, editorName + "_obj", view)
        # self.pathsHeight += y
        self.pathsHeight += self.btnH + p * 2

    def settingsBtnCallback(self, sender):
        path = './settings'
        generateChBox = globalsettings.get('generate', {})
        for editorName in editorNameParser.keys():
            obj = getattr(self.w.view, editorName + "_obj", None)
            if obj is None:
                continue
            if obj.checkbox.get() == 1:
                generateChBox[editorName] = True
            else:
                generateChBox[editorName] = False

        globalsettings['paths'] = self.paths
        globalsettings['generate'] = generateChBox
        exportSettings(globalsettings)

    def getSavingPath(self, sender):
        def _getFolderCallback(path):
            editorName = sender.getTitle()
            self.paths[editorName] = path[0]
            obj = getattr(self.w.view, editorName + "_obj")
            obj.path.set(path[0])
        getFolder(parentWindow=self.w.getNSWindow(), resultCallback=_getFolderCallback)

    def closeSheet(self, sender):
        self.w.close()


class VariableSheet:

    def __init__(self, parentWindow):
        self.snippets = []
        self._varNames = []
        varlist = []
        columnDescriptions = [
            dict(title='order', editable=True),
            dict(title='name', editable=True),
            dict(title='expression', editable=True),
            dict(title='default_value', editable=True),
            dict(title='skip_if_defined', cell=CheckBoxListCell()),
        ]
        self.sheet = Sheet((400, 460), parentWindow)
        self.sheet.list = List((0, 0, -0, -22), varlist,
                               columnDescriptions=columnDescriptions, editCallback=self.listEditCallback)
        self.sheet.closeBtn = SquareButton(
            (0, -22, -0, 22), "close", callback=self.closeSheet)

    def setVarList(self, varlist):
        self.sheet.list.set(varlist)

    def listEditCallback(self, sender):
        varlist = list(sender.get())
        center.postNotification(
            'varListUpdated', data=varlist, observable=self)

    def open(self):
        self.sheet.open()

    def closeSheet(self, sender):
        self.sheet.close()


if __name__ == '__main__':
    from test.testTools import executeVanillaTest
    from debug import DebugWindowController
    # DebugWindowController().show()
    executeVanillaTest(TurboSnippets)
    # TurboSnippets()
