import argparse
import json
import os
from sys import argv, exit

from epubify.utils.ascii_art import SHOW_ASCII, books, error404, llama_small

from .epubify import Epubify
from .systems.pocket import Pocket
from .utils.utils import end_time, process_failed_book, read_json, start_time

TXT_FILE_PREFIX = os.path.join("epubify", "txt_files")
FAILED_BOOKS_CONFIG_PATH = os.path.join(TXT_FILE_PREFIX, "failed_books.json")
FAILED_BOOK_TITLES = os.path.join("epubify", "books", "FAILED_BOOK_TITLES.txt")

# epubify = import_module(name="epubify", package="epubify")
# utils = import_module(name="utils", package="epubify")


def input_prompt():
    print(">> We will ask you for input. If you would rather have a config file, press 1, for manual input, press 2")
    mode = int(input())
    if mode == 1:
        print(">> Enter config file name, after placing it into system/vault/ dir.")
        config_file_name = input()
        with open(config_file_name, "r") as file:
            config_settings = json.load(file)
        return config_settings
    elif mode == 2:
        print(">> Questions, marked with '*' are required.")
        print(">> *Enter URL for the page to convert to epub, surrounded by quotes: ")
        url = input()

        print(">> Enter the name for the new book file: e.g. 'Harry Potter and the order of the phoenix'")
        output_file_name = input()

        print(">> *Enter credentials file name, after placing it into the system/vault/ dir.")
        creds_path = input()

        print(">> Enter book author: ")
        author = input()

        print(">> *Enter book title: ")
        title = input()

        print(
            ">> Enter 'local' mode to save on the machine, or 'remote' "
            "mode to save in a cloud system like dropbox: push ENTER to skip.. "
        )
        mode = input()

        print(">> Enter system ('dropbox' and 'pocket' are currently supported): push ENTER to skip.. ")
        system = input()

        config_settings = {
            "URL": url,
            "title": title,
            "author": author,
            "credsFileName": creds_path,
            "mode": mode,
            "system": system,
            "filePath": output_file_name,
        }

        return config_settings
    else:
        raise ValueError("Invalid choice. Please enter 1 or 2.")


def run_cli():
    parser = argparse.ArgumentParser(description="Welcome to Epubify. " "Use --help to see all the available options.")
    parser.add_argument(
        "-cf",
        help="Path to a JSON config file." "If you provide this, skip all the rest.",
    )
    parser.add_argument("-url", help="Article URL. Add between single quotes.")
    # parser.add_argument('-token',
    #                     help='Dropbox access token. Mandatory if mode is set to `remote` '
    #                          '(see https://www.dropbox.com/developers/apps)')
    parser.add_argument("-author", default="epubify", help="Article author. (Default: `epubify`)")
    parser.add_argument("-title", help="Article author. (Default: Will be fetched from the URL)")
    parser.add_argument(
        "-filepath",
        "-fp",
        help="Directory to store the ebook. (Default: root folder). "
        "If mode is set to `remote`, give the path to the Dropbox folder here.",
    )
    parser.add_argument(
        "-mode",
        default="local",
        help="Mode for storing the converted ebook. Options are: `local` and `remote`." "(Default: `local`)",
    )
    # parser.add_argument('--yes', '-y', action='store_true',
    #                     help='Answer yes to all.')
    # parser.add_argument('--no', '-n', action='store_true',
    #                     help='Answer no to all.')
    parser.add_argument("--default", "-d", action="store_true", help="Take default answer on all.")
    args = parser.parse_args()

    if len(argv) < 1:
        parser.print_help()
        exit()

    if not args.cf:
        if not args.url:
            print(">> URL is required. Use \n" "--url 'https://my_url'")
            exit()

        if args.mode == "local" and not args.filepath:
            args.filepath = "~/Downloads"
        elif args.mode == "remote" and not args.filepath:
            args.filepath = "/"
        else:
            pass

        if args.mode == "remote":
            print(">> Dropbox token is required for remote mode.")
            exit()
        settings = args.__dict__
    else:
        print(">> Reading data from config file %s" % args.cf)
        settings = read_json(file_path=str(args.cf))
    return settings


def process_book(from_file, preprocess=True, **config):
    """Processing book by book separately

    :param preprocess: Whether or not to apply preprocessing and cleaning of the data.
    Set it to False if reading from txt file which is assumed to not require this
    :type preprocess: Bool

    :param config: config per article
    :param config: dict
    """
    epub = Epubify(from_file, **config)

    try:
        if from_file:
            ebook = epub.fetch_content_from_text_file()
        else:
            ebook = epub.fetch_html_text()

        if preprocess:
            ebook = ebook.preprocess_text()

        ebook = epub.create_book()
        epub.save_book(book=ebook, sys=epub.system_to)
        if SHOW_ASCII:
            print(llama_small)
    except Exception as err:
        print(">> SOMETHING FAILED when processing the article: %s \n SKIPPING ARTICLE." % err)
        if SHOW_ASCII:
            print(error404)
        process_failed_book(
            book=epub,
            titles_path=FAILED_BOOK_TITLES,
            books_config_path=FAILED_BOOKS_CONFIG_PATH,
            prefix=TXT_FILE_PREFIX,
        )
    print("=" * 100)


def run(**config):
    src_system = config["from"]["system"]

    articles, from_file, process = get_system_config(config, src_system)

    for count, article in enumerate(articles):
        print(">> Processing book {} of {}.. ".format(count, len(articles)))
        config["article"] = article
        print("--------")
        process_book(from_file, process, **config)

    if SHOW_ASCII:
        print(books)
        print(
            """
        The articles that failed to be processed (if any) are stored in '{}'
        A config file ready to use has been generated. To run it and process the failed books (where possible), run:
        python -m epubify -cf '{}'
        """.format(
                FAILED_BOOK_TITLES, FAILED_BOOKS_CONFIG_PATH
            )
        )


def get_system_config(config, src_system):
    if src_system == "pocket":
        EPUBIFY_KEY = "92033-7e774220ee6e0a96bc04ed2d"
        REDIRECT_URL = "http://worldofinspiration.net/epubify.html"
        access_code = None
        # TODO save access code in json file and read it from there

        pocket_client = Pocket(EPUBIFY_KEY, REDIRECT_URL, access_code)
        articles = pocket_client.get_article_list()
        from_file = False
        process = config.get(config["from"].get("preprocess", True), True)

    elif src_system == "url" and config["articles"]:
        articles = config["articles"]
        from_file = False
        process = config.get(config["from"].get("preprocess", True), True)

    elif src_system == "txt" and config["articles"]:
        articles = config["articles"]
        from_file = True
        process = config.get(config["from"].get("preprocess", False), False)
    else:
        raise KeyError(
            "You are either missing the 'articles' key in your config "
            "or have entered unsupported source system, other than 'url', 'txt', or 'pocket'"
        )

    return articles, from_file, process


def entry_point():
    # TODO: CREATE AN EXECUTABLE with pyinstaller
    # TODO: Loop over multiple files
    # https://realpython.com/pyinstaller-python/#preparing-your-project

    # TODO: Once reading from pocket is finished, reconsider this argument parser. May be not required anymore
    settings = run_cli()

    start_time()
    run(**settings)
    end_time()
    # https://stackoverflow.com/questions/1325581/how-do-i-check-if-im-running-on-windows-in-python
    # https://medium.com/dreamcatcher-its-blog/making-an-stand-alone-executable-from-a-python-script-using-pyinstaller-d1df9170e263


if __name__ == "__main__":
    entry_point()
