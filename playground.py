# coding=utf-8
from __future__ import unicode_literals
from pprint import pprint
# sys.setdefaultencoding("utf8")

dddddd = [{"abbreviation": "testmain", "alfred_name": "ctestmain", "description": "create __main__ document", "text": "def test()\n    # codehere\n\nif __main__ == '__name__':\n    test()", "variables": [{"default_value": "", "expression": "", "name": "codehere", "skip_if_defined": ""}]}, {"abbreviation": "defm", "alfred_name": "defm", "description": "create method", "text": "    def *method*(self, *args*):\n        \"\"\"\n        *method* docstring\n        \"\"\"", "variables": []}, {"abbreviation": "~2", "description": "…", "text": "", "variables": []}]


print(dddddd)