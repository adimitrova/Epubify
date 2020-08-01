import json, time, logging
from uuid import uuid4
from os import path, rename

_start_time = time.time()


def system_import(sys, **config):
    module_name = "drop_box" if sys == "dropbox" else sys.lower()
    try:
        from importlib import import_module

        class_ = getattr(
            import_module("epubify.systems.%s" % module_name), sys.capitalize()
        )
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
    (t_hour,t_min) = divmod(t_min, 60)
    print('Time passed: {}hour:{}min:{}sec'.format(t_hour,t_min,t_sec))


def set_global(key, value):
    globals()[key] = value


def append_keyvalue_to_json_file(file_path, key, value):
    # Modify the original config file with pocket auth code once authenticated, to avoid re-authentication
    with open(file_path, "r") as cfi:
        config_file_content = json.load(cfi)
        config_file_content[key] = value

    # create randomly named temporary file to avoid
    # interference with other thread/asynchronous request
    tempfile = path.join(path.dirname(file_path), str(uuid4()))
    with open(tempfile, "w") as cfo:
        json.dump(config_file_content, cfo, indent=4)

    # rename temporary file replacing old file
    rename(tempfile, file_path)


def read_txt(file_path):
    with open(file_path, "r") as file:
        text = file.read()
    return text


def read_json(file_path, key_name=None):
    with open(file_path, "r") as file:
        content = json.load(file)
    if not key_name:
        return content
    else:
        return content[key_name]
