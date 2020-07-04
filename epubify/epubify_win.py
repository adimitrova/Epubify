# coding=utf-8

import requests
from bs4 import BeautifulSoup
import mkepub
import re
import logging
from os import getcwd, path
import dropbox
import regex
from unidecode import unidecode

# logging
# LOG = "output.log"
# logging.basicConfig(filename=LOG, filemode="w", level=logging.INFO)
# logger = logging.getLogger(__name__)

def process_chunk(chunk):
    new_chunk = ""
    if len(chunk.split(" ")) < 4:
        # Ignore lines with few words, they are likely unrelated
        pass
    elif len(chunk.split(" ")) < 15:
        # Keep small lines / sentences, could be related, but separate them from main text to make them more visible.
        new_chunk = "\n" + chunk
    else:
        # add the actual text to the new_chunks string.
        new_chunk = " " + chunk
    return new_chunk

def encode(chunk):
    temp_book = mkepub.Book(title="test_encoding", author='epubify')
    try:
        temp_book.add_page("test_encoding", chunk)
        return chunk
    except UnicodeEncodeError as encode_err:
        chunk_no_special_chars = ""
        for word in chunk.split():
            try:
                temp_book.add_page("test_encoding", word)
                chunk_no_special_chars += word + " "
            except UnicodeEncodeError as encode_err:
                temp_word = ""
                for char in list(word):
                    try:
                        temp_book.add_page("test_encoding", char)
                        temp_word += char
                    except UnicodeEncodeError as encode_err:
                        temp_word += "_"
                chunk_no_special_chars += temp_word + " "
        # print("====== AFTER ======> %s " % chunk_no_special_chars)
    return chunk_no_special_chars

def cleanup(chunk=None):
    text = """cruisers USS\xc2\xa0Bainbridge, USS\xc2\xa0Long Beach, and USS\xc2\xa0Enterprise, the first 
    nuclear-powered aircraft carrier. Picture taken in 1964 during a record setting voyage of 26,540\xc2\xa0nmi 
    (49,152\xc2\xa0km) around the world in 65 days without refueling. Crew members are spelling out Einstein's 
    mass-energy equivalence formula E\xc2\xa0=\xc2\xa0mc2 on the flight deck."\nGlobal civilian electricity 
    generation by source. Some 23,816 TWh total.[4] """
    regex_clutter = re.compile('(\[[0-9]+\]|\[[a-z]+\]|\[редактиране \| редактиране на кода\])')
    if regex_clutter.search(chunk):
        chunk = re.sub(regex_clutter, '', chunk)
    return chunk

def epubify(URL, fileName, DROPBOX_ACCESS_TOKEN=None, dropboxPath=None, localPath=None):

    response = requests.get(URL, verify=False)

    soup = BeautifulSoup(response.content, features="html.parser")

    # kill all script and style elements
    for element in soup(["script", "style", "meta", "footer", "img", "li", "ul"]):
        element.extract()    # rip it out

    print(">> Getting the text..")
    text = soup.get_text().strip('\n')

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines() if len(line) > 3)

    print(">> Processing the text..")
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

    new_chunks = ""

    for ch in chunks:
        # check if occurrence of the pattern is found in the chunk
        if regex.search(r'[а-яА-Я]', ch):
            clean_chunk = cleanup(ch)
            new_chunks += process_chunk(clean_chunk)
        else:
            clean_chunk = cleanup(ch)
            unencoded_chunk = process_chunk(clean_chunk)
            encoded_chunk = encode(unencoded_chunk)
            new_chunks += encoded_chunk

    final_content = new_chunks

    # print(final_content)

    # TODO: Add more cleansing logic

    # ================================== prepare to save as epub ===============================

    print(">> Done!")

    if file_name:
        title = file_name
    else:
        raise AttributeError("You must enter the name for the file.")

    book = mkepub.Book(title=title, author='Article')

    book.add_page(title, final_content)

    # print(f"\n========== CONTENT =========== {final_content} \n============== END OF CONTENT =============\n")

    if localPath:
        local_path = localPath + '\\' + title + '.epub'
    else:
        local_path = "{}/books/{}.epub".format(getcwd(), title)

    try:
        book.save(local_path)
        print(">> Saved (locally) at: {}".format(local_path))
    except FileExistsError as err:
        print(">> A file with this name already exists at {}".format(local_path))

if __name__ == '__main__':
    creds_file_path = path.abspath(path.join(__file__, "../../.."))+"/credentials.json"

    # with open(creds_file_path) as creds_file:
        # creds_content = json.load(creds_file)

    # url = input("Copy/Paste the URL for the epub file: ")
    url = "https://novini.bg/bylgariya/politika/527075"
    # url = "https://en.wikipedia.org/wiki/Nuclear_power"
    # url = "http://kunststube.net/encoding/"

    # dropbox_token = input("Create a dropbox app and paste the access token here: ")
    # dropbox_token = creds_content['epubify']['access_token']

    # dropbox_path = '/Dropbox/Apps/Dropbox PocketBook/Articles'
    local_path = r"D:\Dropbox\Apps\Dropbox PocketBook\Articles"
    # save_path = input("Enter linux-like path where the file will be saved: ")
    file_name = 'politika'

    epubify(url, file_name, localPath=local_path)
    # cleanup()
    # encode("test")


# https://stackoverflow.com/questions/1325581/how-do-i-check-if-im-running-on-windows-in-python
# https://medium.com/dreamcatcher-its-blog/making-an-stand-alone-executable-from-a-python-script-using-pyinstaller-d1df9170e263