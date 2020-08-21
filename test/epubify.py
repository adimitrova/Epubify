import unittest
import epubify
from epubify import epubify
from epubify.utils import utils
from os import getcwd

configs = {
    "txt_to_local": {
        "from": {
            "system": "txt",
            "preprocess": True
        },
        "to": {
            "mode": "local"
        },
        "article":
            {
                "title": "How to Dismantle a Democracy",
                "content": utils.read_txt("test/data/how_to_dismantle_a_democracy_the_case_of_bulgaria.txt"),
                "author": "openDemocracy"
            }
    },
    "pocket_to_local": {
        'article': {'author': 'epubify',
                    'title': 'Как кокичето стана лекарство',
                    'url': 'https://www.obekti.bg/nauka/kak-kokicheto-stana-lekarstvo'},
        'credsFileName': 'my_keys.json',
        'from': {'system': 'pocket'},
        'to': {'filePath': '/Stuff/epubify',
               'mode': 'remote',
               'saveMode': 'overwrite',
               'system': 'dropbox'}},
    "pocket_to_dropbox": {
        "from": {
            "system": "pocket"
        },
        "to": {
            "mode": "remote",
            "filePath": "/Stuff/epubify",
            "system": "dropbox",
            "saveMode": "overwrite"
        },
        "credsFileName": "my_keys.json"
    }
}


class TestEpubify(unittest.TestCase):
    def setUp(self):
        print("Creating epubify objects")
        self.epubify1 = epubify.Epubify(**configs.get("txt_to_local"))
        self.epubify2 = epubify.Epubify(**configs.get("pocket_to_local"))
        self.epubify3 = epubify.Epubify(**configs.get("pocket_to_dropbox"))

    def testFileName(self):
        print("Test %s" % "testFileName")
        actual = self.epubify1.file_path
        expected = getcwd() + "/epubify/books/how_to_dismantle_a_democracy.epub"
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    # python -m unittest -v test
    unittest.main()
