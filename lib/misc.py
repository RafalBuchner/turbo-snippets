
import AppKit

import sys
import os
import subprocess
import re
from plistlib import readPlist, writePlist
# from fontTools.misc.transform import Transform


# ==========
# = errors =
# ==========


class SnippetCreatorError(TypeError):
    pass


# =================
# = default tools =
# =================

def getDefault(key, defaultValue=None):
    """
    Get a value from the user default for a key.
    """
    defaultsFromFile = AppKit.NSUserDefaults.standardUserDefaults()
    return defaultsFromFile.get(key, defaultValue)


def setDefault(key, value):
    """
    Set a value to the user defaults for a given key.
    """
    defaultsFromFile = AppKit.NSUserDefaults.standardUserDefaults()
    defaultsFromFile.setObject_forKey_(value, key)


def _getNSDefault(key, defaultValue=None):
    data = getDefault(key, defaultValue)
    if isinstance(data, AppKit.NSData):
        return AppKit.NSUnarchiver.unarchiveObjectWithData_(data)
    return data


def _setNSDefault(key, value):
    data = AppKit.NSArchiver.archivedDataWithRootObject_(value)
    setDefault(key, data)


def getFontDefault(key, defaultValue=None):
    return _getNSDefault(key, defaultValue)


def setFontDefault(key, font):
    _setNSDefault(key, font)


def getColorDefault(key, defaultValue=None):
    return _getNSDefault(key, defaultValue)


def setColorDefault(key, color):
    _setNSDefault(key, color)



# ==============
# = text tools =
# ==============

def findVariables(text):
    if '$' not in text:
        return None
    varNames = re.findall(r'\$(.*?)\$', text)
    return varNames

def renameVariables(text, oldvarNames, newvarNames):
    if '$' not in text or len(newvarNames) == 0:
        return
    for i, varName in enumerate(oldvarNames):
        text = "$".join([newvarNames[i] if fraze==varName else fraze for fraze in text.split('$')])
    return text

# def optimizePath(path):
#     if path.startswith("http"):
#         return path
#     path = os.path.expanduser(path)
#     if not os.path.isabs(path):
#         path = os.path.abspath(path)
#     return path


# ================
# = number tools =
# ================

# def formatNumber(value, decimals=2):
#     value = float(value)
#     if value.is_integer():
#         return "%i" % value
#     value = round(value, decimals)
#     return "%s" % value


# ===============
# = color tools =
# ===============

# def cmyk2rgb(c, m, y, k):
#     """
#     Convert cmyk color to rbg color.
#     """
#     r = 1.0 - min(1.0, c + k)
#     g = 1.0 - min(1.0, m + k)
#     b = 1.0 - min(1.0, y + k)
#     return r, g, b


# def rgb2cmyk(r, g, b):
    
#     Convert rgb color to cmyk color.
    
#     c = 1 - r
#     m = 1 - g
#     y = 1 - b
#     k = min(c, m, y)
#     c = min(1, max(0, c - k))
#     m = min(1, max(0, m - k))
#     y = min(1, max(0, y - k))
#     k = min(1, max(0, k))
#     return c, m, y, k


# ==============
# = file tools =
# ==============

def isPDF(url):
    if not isinstance(url, AppKit.NSURL):
        url = AppKit.NSURL.fileURLWithPath_(url)
    if url.pathExtension().lower() != "pdf":
        return False, None
    doc = AppKit.PDFDocument.alloc().initWithURL_(url)
    return doc is not None, doc


# =============

def stringToInt(code):
    import struct
    return struct.unpack('>l', code)[0]


def nsStringLength(s):
    return len(s.encode("utf-16-be")) // 2


# ============
# =  format  =
# ============



# ============
# =  export  =
# ============

fileFormat = 'turboSnippets'
settingFormat = 'turboSnippetsSettings'

def importSettings():
    path = 'settings.' + settingFormat
    if os.path.exists(path):
        if path.split('.')[-1] == settingFormat:
            settings = readPlist(path)
            return settings
    return None

def exportSettings(data):
    path = 'settings.'+ settingFormat
    writePlist(data, path)

def importFromTurboSnippets(path):
    if path:
        if path.split('.')[-1] == fileFormat:
            turboSnippets = readPlist(path)
            return turboSnippets
    return None
        
def exportToTurboSnippets(path, data):
    print(path)
    print(data)
    writePlist(data, path)

# ============
# = warnings =
# ============

# class Warnings(object):

#     def __init__(self):
#         self._warnMessages = set()
#         self.shouldShowWarnings = False

#     def resetWarnings(self):
#         self._warnMessages = set()

#     def warn(self, message):
#         if not self.shouldShowWarnings:
#             return
#         if message in self._warnMessages:
#             return
#         sys.stderr.write("*** DrawBot warning: %s ***\n" % message)
#         self._warnMessages.add(message)


# warnings = Warnings()


# class VariableController(object):

#     def __init__(self, attributes, callback, document=None):
#         import vanilla
#         self._callback = callback
#         self._attributes = None
#         self.w = vanilla.FloatingWindow((250, 50))
#         self.buildUI(attributes)
#         self.w.open()
#         if document:
#             self.w.assignToDocument(document)
#         self.w.setTitle("Variables")

#     def buildUI(self, attributes):
#         import vanilla
#         if self._attributes == attributes:
#             return
#         self._attributes = attributes
#         if hasattr(self.w, "ui"):
#             del self.w.ui
#         self.w.ui = ui = vanilla.Group((0, 0, -0, -0))
#         y = 10
#         labelSize = 100
#         gutter = 5
#         for attribute in self._attributes:
#             uiElement = attribute["ui"]
#             name = attribute["name"]
#             args = dict(attribute.get("args", {}))
#             height = 19
#             # adjust the height if a radioGroup is vertical
#             if uiElement == "RadioGroup":
#                 if args.get("isVertical", True):
#                     height = height * len(args.get("titles", [""]))
#             # create a label for every ui element except a checkbox
#             if uiElement not in ("CheckBox", "Button"):
#                 # create the label view
#                 label = vanilla.TextBox((0, y + 2, labelSize - gutter, height), "%s:" % name, alignment="right", sizeStyle="small")
#                 # set the label view
#                 setattr(ui, "%sLabel" % name, label)
#             else:
#                 if "title" not in args:
#                     args["title"] = name
#             # check the provided args and add required keys
#             if uiElement == "ColorWell":
#                 # a color well needs a color to be set
#                 # no size style
#                 if "color" not in args:
#                     args["color"] = AppKit.NSColor.blackColor()
#             elif uiElement == "TextEditor":
#                 # different control height
#                 # no size style
#                 height = attribute.get("height", 75)
#             else:
#                 # all other get a size style
#                 args["sizeStyle"] = "small"
#             # create the control view
#             attr = getattr(vanilla, uiElement)((labelSize, y, -10, height), callback=self.changed, **args)
#             # set the control view
#             setattr(ui, name, attr)
#             y += height + 6
#         # resize the window according the provided ui elements
#         self.w.resize(250, y)

#     def changed(self, sender):
#         self.documentWindowToFront()
#         if self._callback:
#             self._callback()

#     def get(self):
#         data = {}
#         for attribute in self._attributes:
#             if attribute["ui"] in ("Button", ):
#                 continue
#             name = attribute["name"]
#             data[name] = getattr(self.w.ui, name).get()
#         return data

#     def show(self):
#         self.w.show()

#     def documentWindowToFront(self, sender=None):
#         self.w.makeKey()


# def executeExternalProcess(cmds, cwd=None):
#     r"""
#         >>> stdout, stderr = executeExternalProcess(["which", "ls"])
#         >>> stdout
#         '/bin/ls\n'
#         >>> assert stdout == '/bin/ls\n'
#         >>> executeExternalProcess(["which", "fooooo"])
#         Traceback (most recent call last):
#             ...
#         RuntimeError: 'which' failed with error code 1
#         >>> stdout, stderr = executeExternalProcess(["python", "-S", "-c", "print('hello')"])
#         >>> stdout
#         'hello\n'
#     """
#     p = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, universal_newlines=True)
#     stdoutdata, stderrdata = p.communicate()
#     assert p.returncode is not None
#     if p.returncode != 0:
#         sys.stdout.write(stdoutdata)
#         sys.stderr.write(stderrdata)
#         raise RuntimeError("%r failed with error code %s" % (os.path.basename(cmds[0]), p.returncode))
#     return stdoutdata, stderrdata


# def getExternalToolPath(root, toolName):
#     toolPath = os.path.join(root, toolName)
#     if not os.path.exists(toolPath):
#         toolPath = AppKit.NSBundle.mainBundle().pathForResource_ofType_(toolName, None)
#         if toolPath is None or not os.path.exists(toolPath):
#             import drawBot
#             root = os.path.dirname(drawBot.__file__)
#             toolPath = os.path.join(root, "..", "Resources", "externalTools", toolName)
#     return toolPath


# # =================
# # = caching tools =
# # =================

# _memoizeCache = dict()


# def clearMemoizeCache():
#     # clears all memoized caches
#     # this is intended as the usage of memoize is made per context
#     _memoizeCache.clear()


# def memoize(function):
#     """
#     Memoize a function's return value with the function's arguments.
#     The next time a function is called with the same arguments, the cache is returned.
#     Example usage:
#         @memoize
#         def addNumbers(first, second):
#             return first + second
#         # The first time this function is called the calculation will be made,
#         # and and the result will be stored in the cache dict as [first, second]: returnValue
#         # From then on, this value will be returned when the same argument is made to the addNumbers function
#     """
#     def wrapper(*args):
#         key = (function, args)
#         if key in _memoizeCache:
#             return _memoizeCache[key]
#         else:
#             result = function(*args)
#             _memoizeCache[key] = result
#             return result
#     return wrapper


if __name__ == "__main__":
    path = '/Users/rafaelbuchner/repos/myTools/snippetCreator/lib/output/turbosnippets/CodePython.turboSnippets'
    importFromTurboSnippets(path)

    