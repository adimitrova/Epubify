import json
from uuid import uuid4
from os import path, rename


def system_import(sys, **config):
    module_name = 'drop_box' if sys == 'dropbox' else sys.lower()
    try:
        from importlib import import_module
        class_ = getattr(import_module("epubify.systems.%s" % module_name), sys.capitalize())
        system_instance = class_(**config)
    except ImportError as e:
        print(e)

    return system_instance


def set_global(key, value):
    globals()[key] = value


def append_keyvalue_to_json_file(file_path, key, value):
    # Modify the original config file with pocket auth code once authenticated, to avoid re-authentication
        with open(file_path, 'r') as cfi:
            config_file_content = json.load(cfi)
            config_file_content[key] = value

        # create randomly named temporary file to avoid
        # interference with other thread/asynchronous request
        tempfile = path.join(path.dirname(file_path), str(uuid4()))
        with open(tempfile, 'w') as cfo:
            json.dump(config_file_content, cfo, indent=4)

        # rename temporary file replacing old file
        rename(tempfile, file_path)


def read_txt(file_path):
    with open(file_path, 'r') as file:
        text = file.read()
    return text


def read_json(file_path):
    with open(file_path, 'r') as file:
        content = json.load(file)
    return content