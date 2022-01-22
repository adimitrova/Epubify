# -*- coding: utf-8 -*-
# import beautifulsoup4
import mkepub, re, dropbox, requests
from os import getcwd, path
from bs4 import BeautifulSoup
import urllib3
from importlib import import_module
from .utils.utils import read_txt, system_import
import os

# ascii_art = import_module(name="ascii_art", package="epubify")
# utils = import_module(name="utils", package="epubify")


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Epubify(object):
    # TODO: replace all prints with logger
    # TODO: Rework for cases of multiple articles at once OR keep this class as a single article at a time
    # Maybe the latter is better

    def __init__(self, from_file, **config):
        self.settings = config

        self.system_from = config["from"].get("system", None)
        self.system_to = config["to"].get("system", None)
        self.mode = config["to"]["mode"]
        self.file_path = config["to"].get("filePath", None)
        self.book_content = (
            ""  # initial state of the text is empty, gets replaces in fetch_html_text()
        )

        if "article" not in config.keys():
            print("Initiating Epubify instance w/o article data.")
        else:
            if from_file:
                self.url = config["article"]["txtPath"] 
            else:
                self.url = config["article"]["url"].strip('"').strip("'")
            
            pattern = re.compile("([^\s\w]|)+")
            # self.title = config['article']['title'].lower()
            self.title = pattern.sub("", config["article"]["title"].lower())
            self.title = re.sub(r"\s+", "_", self.title)
            self.author = config["article"].get("author", "epubify")

            # TODO: fix _generate_file_path
            if not self.file_path:
                self.file_path = self._generate_file_path()
            self.settings["filePath"] = self.file_path
            # update filePath to the dict which will be passed onto the save_book method
            print(">> The book will be saved at: [%s] " % self.file_path)

    def fetch_content_from_text_file(self):
        self.book_content = read_txt(self.url)

        return self

    def get_book_title(self):
        return self.title, self.author

    def fetch_html_text(self):
        try:
            response = requests.get(self.url, verify=False)
            soup = BeautifulSoup(response.content, features="html.parser")

            # kill all script and style elements
            # TODO: Add a check for text in the "meta" element and fetch the text
            for element in soup(
                ["script", "style", "meta", "footer", "img", "li", "ul"]
            ):
                element.extract()  # rip it out

            print(">> Getting the HTML content..")
            text = soup.get_text().strip("\n")
            print(">> HTML content fetched and stored safely.")
            self.book_content = text
            
            return self  # Note: Enables chaining of another method after this one. (called cascading)
        except requests.exceptions.RequestException as err:
            print(
                ">> ERROR when fetching HTML content for article %s: %s \n SKIPPING ARTICLE."
                % (self.file_path, err)
            )
            self.book_content = None
        except Exception as err:
            print(
                ">> ERROR when fetching HTML content for article %s: %s \n SKIPPING ARTICLE."
                % (self.file_path, err)
            )
            self.book_content = None

    def preprocess_text(self):
        # TODO: Add more cleansing logic
        # TODO: break into lines and remove leading and trailing space on each
        lines = (
            line.strip() for line in self.book_content.splitlines() if len(line) > 3
        )

        reg_ex = re.compile(
            "(\[[0-9]+\]|\[[a-z]+\]|\[редактиране \| редактиране на кода\])"
        )
        print(">> Processing the text..")
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        new_chunks = ""
        for ch in chunks:
            # check if occurrence of the pattern is found in the chunk
            if re.search(reg_ex, ch):
                match_chunk = re.sub(reg_ex, "", ch)
                if len(match_chunk.split(" ")) < 4:
                    # Ignore lines with few words, they are likely unrelated
                    pass
                elif len(match_chunk.split(" ")) < 15:
                    # Keep small lines / sentences, could be related, but separate them from main text to make them more visible.
                    new_chunks += "\n" + match_chunk
                else:
                    # add the actual text to the new_chunks string.
                    new_chunks += " " + match_chunk
            else:
                if len(ch.split(" ")) < 4:
                    # Ignore lines with few words, they are likely unrelated
                    pass
                elif len(ch.split(" ")) < 15:
                    # Keep small lines / sentences, could be related, but separate them from main text to make them more visible.
                    new_chunks += "\n" + ch
                else:
                    # add the actual text to the new_chunks string.
                    new_chunks += " " + ch

        # reg_ex = re.compile(r'(\[[0-9]+\]|\[[a-z]+\]|\[редактиране \| редактиране на кода\])')
        final_content = new_chunks
        final_content = re.sub(reg_ex, "", final_content)
        print(">> HTML content processed and saved.")
        self.book_content = final_content
        return self

    def create_book(self):
        print(">> Creating the book.. ")
        book = mkepub.Book(title=self.title, author=self.author)
        # TODO we have a problem with not utf encoding content
        book.add_page(self.title, self.book_content)
        return book

    def save_book(self, book, sys=None):
        if self.mode == "local":
            self._save_book_locally(book)
        elif self.mode == "remote":
            self._save_book_remotely(book, sys)
        print(">> Done!")

    ######## PRIVATE METHODS ##########
    def _generate_file_path(self):
        if self.mode == "local":
            # local mode nad no path provided = saved in current projects' folder in the books dir
            if getcwd().endswith("Epubify"):
                file_path = os.path.join(getcwd(),'epubify', 'books', f"{self.title}.epub" )
            elif getcwd().endswith("epubify"):
                file_path = os.path.join(getcwd(),'books', f"{self.title}.epub" )

        if self.mode == "remote":
            # remote saving. For now only in dropbox:
            if self.system_to == "dropbox":
                print("remote mode saving to dropbox")
                file_path = "/"  # root folder
                # TODO: add check for OS and modify accordingly
        return file_path

    def _save_book_locally(self, book):
        try:
            book.save(self.file_path)
            print(">> Saved (locally) at: {}".format(self.file_path))
        except FileExistsError:
            print(
                ">> A file with this name already exists at [{}]. \nOVERRIDE? (y/n)".format(
                    self.file_path
                )
            )
            override = input()
            if override == "y":
                print(">> Overriding the book")
                from os import remove

                remove(self.file_path)
                book.save(self.file_path)
            else:
                print(">> Skip saving the book..")
                pass

    def _save_book_remotely(self, book, sys):
        # TODO: save to system (pocket, dropbox etc)
        print(">> Import system [%s]" % sys)
        target_system = system_import(sys, **self.settings)
        import inspect

        if sys == "dropbox":
            target_system.save_book(book)
