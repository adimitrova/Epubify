import json
import time
from os import path, rename
from uuid import uuid4

_start_time = time.time()


def set_global(key, value):
    globals()[key] = value


def system_import(sys, **config):
    module_name = "drop_box" if sys == "dropbox" else sys.lower()
    try:
        from importlib import import_module

        class_ = getattr(import_module("epubify.systems.%s" % module_name), sys.capitalize())
        system_instance = class_(**config)
    except ImportError as e:
        print(e)
    return system_instance


def start_time():
    global _start_time
    _start_time = time.time()


def end_time():
    t_sec = round(time.time() - _start_time)
    (t_min, t_sec) = divmod(t_sec, 60)
    (t_hour, t_min) = divmod(t_min, 60)
    print("Time passed: {}hour:{}min:{}sec".format(t_hour, t_min, t_sec))


def failed_books_conf_exists(file_path):
    if path.exists(file_path):
        return True
    else:
        return False


def create_failed_books_config(file_path):
    config = {
        "from": {
            "system": "txt",
        },
        "to": {"mode": "local"},
        "articles": [],
    }
    with open(file_path, 'w', encoding="utf-8") as oFile:
        json.dump(config, oFile)


def process_failed_book(book, titles_path, books_config_path, prefix):
    book_title = book.get_book_title()[0]
    # write the book title to the final list of failed articles
    append_to_file(titles_path, "\t - " + book_title)
    if not failed_books_conf_exists(file_path=books_config_path):
        create_failed_books_config(file_path=books_config_path)
    # write the book content as a TXT file
    append_to_file(file_path=prefix + "{}.txt".format(book_title), file_content=book.book_content)

    # Fetch the current failed books config content
    current_config = read_json(file_path=books_config_path)
    current_config["articles"].append(
        {"title": book_title, "txtPath": prefix + "{}.txt".format(book_title), "author": "epubify"}
    )
    # TODO: Fix this article update code!!!!!
    # override the config file with the new version
    print(">> The config file contains now [{}] failed books.".format(len(current_config["articles"])))
    write_json(books_config_path, current_config)
    return True


def append_keyvalue_to_json_file(file_path, key, value):
    # Modify the original config file with pocket auth code once authenticated, to avoid re-authentication
    with open(file_path, "r", encoding="utf-8") as cfi:
        config_file_content = json.load(cfi)
        config_file_content[key] = value

    # create randomly named temporary file to avoid
    # interference with other thread/asynchronous request
    tempfile = path.join(path.dirname(file_path), str(uuid4()))
    with open(tempfile, "w", encoding="utf-8") as cfo:
        json.dump(config_file_content, cfo, indent=4)

    # rename temporary file replacing old file
    rename(tempfile, file_path)


def read_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    return text


def read_json(file_path, key_name=None):
    with open(file_path, "r", encoding="utf-8") as file:
        content = json.load(file)

    if key_name is not None:
        return content[key_name]

    return content

def write_json(file_path, file_content):
    with open(file_path, "w", encoding="utf-8") as outfile:
        json.dump(file_content, outfile)


def append_to_file(file_path, file_content):
    with open(file_path, 'a', encoding='utf-8') as oFile:
        oFile.write(file_content + '\n')

