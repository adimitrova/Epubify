import json, argparse
from sys import argv, exit
from .epubify import Epubify
from .utils.utils import read_json, read_txt, start_time, end_time, write_to_file
from epubify.utils.ascii_art import books, llama_small, error404


# epubify = import_module(name="epubify", package="epubify")
# utils = import_module(name="utils", package="epubify")


def input_prompt():
    print(
        ">> We will ask you for input. If you would rather have a config file, press 1, for manual input, press 2"
    )
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

        print(
            ">> Enter the name for the new book file: e.g. 'Harry Potter and the order of the phoenix'"
        )
        output_file_name = input()

        print(
            ">> *Enter credentials file name, after placing it into the system/vault/ dir."
        )
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

        print(
            ">> Enter system ('dropbox' and 'pocket' are currently supported): push ENTER to skip.. "
        )
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
    parser = argparse.ArgumentParser(
        description="Welcome to Epubify. "
        "Use --help to see all the available options."
    )
    parser.add_argument(
        "-cf",
        help="Path to a JSON config file." "If you provide this, skip all the rest.",
    )
    parser.add_argument("-url", help="Article URL. Add between single quotes.")
    # parser.add_argument('-token',
    #                     help='Dropbox access token. Mandatory if mode is set to `remote` '
    #                          '(see https://www.dropbox.com/developers/apps)')
    parser.add_argument(
        "-author", default="epubify", help="Article author. (Default: `epubify`)"
    )
    parser.add_argument(
        "-title", help="Article author. (Default: Will be fetched from the URL)"
    )
    parser.add_argument(
        "-filepath",
        "-fp",
        help="Directory to store the ebook. (Default: root folder). "
        "If mode is set to `remote`, give the path to the Dropbox folder here.",
    )
    parser.add_argument(
        "-mode",
        default="local",
        help="Mode for storing the converted ebook. Options are: `local` and `remote`."
        "(Default: `local`)",
    )
    # parser.add_argument('--yes', '-y', action='store_true',
    #                     help='Answer yes to all.')
    # parser.add_argument('--no', '-n', action='store_true',
    #                     help='Answer no to all.')
    parser.add_argument(
        "--default", "-d", action="store_true", help="Take default answer on all."
    )
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


def process_book(preprocess=True, **config):
    """ Processing book by book separately

    :param preprocess: Whether or not to apply preprocessing and cleaning of the data.
    Set it to False if reading from txt file which is assumed to not require this
    :type preprocess: Bool

    :param config: config per article
    :param config: dict
    """
    epub = Epubify(**config)
    try:
        if preprocess and "url" not in config["article"].keys():
            ebook = epub.preprocess_text().create_book()
        elif preprocess:
            ebook = epub.fetch_html_text().preprocess_text().create_book()
        else:
            ebook = epub.create_book()
        epub.save_book(book=ebook, sys=epub.system_to)
        print(llama_small)
    except Exception as err:
        print(
            ">> SOMETHING FAILED when processing the article: %s \n SKIPPING ARTICLE."
            % err
        )
        print(error404)
        write_to_file('epubify/books/FAILED.txt', "\t - " + epub.get_book_title()[0])
    print("=" * 100)


def run(**config):
    src_system = config['from']['system']
    start_time()
    if src_system == 'pocket':
        article_dict = Epubify.get_pocket_articles(**config)
        count, total = 0, len(article_dict.items())
        for item in article_dict.items():
            print(">> Processing book {} of {}.. ".format(count, total))
            config["article"] = {"url": item[1], "title": item[0], "author": "epubify"}
            # TODO: feature for saving all this in the config for the user to be able to delete
            #  the articles they don't want and resubmit the file
            process_book(**config)
            count += 1
    elif src_system == "url" and config["articles"]:
        # TODO: Finish this, top prio
        print("multiple articles from url")
    elif src_system == "txt":
        articles = config.pop("articles")
        for item in articles:
            print(
                ">> Creating an ebook from a TXT file. Assuming the text is already "
                "in a human-readable format and won't be preprocessed."
                "To override this behaviour, add a preprocess key in the config, set it to 'true'"
            )
            content = read_txt(item["txtPath"])
            config["article"] = {
                "bookContent": content,
                "title": item.get("title", "epubify_article"),
                "author": item.get("author", "epubify"),
            }
            print(content)
            process_book(preprocess=config["from"].pop("preprocess", False), **config)
    else:
        raise KeyError(
            "You are either missing the 'articles' key in your config "
            "or have entered unsupported source system, other than 'url', 'txt', or 'pocket'"
        )
    print(books)
    print("The articles that failed to be processed (if any) are stored in 'epubify/books/FAILED.txt'.")
    end_time()
   

def entry_point():
    # TODO: CREATE AN EXECUTABLE with pyinstaller
    # TODO: Loop over multiple files
    ## https://realpython.com/pyinstaller-python/#preparing-your-project

    # TODO: Once reading from pocket is finished, reconsider this argument parser. May be not required anymore
    settings = run_cli()
    run(**settings)

    # https://stackoverflow.com/questions/1325581/how-do-i-check-if-im-running-on-windows-in-python
    # https://medium.com/dreamcatcher-its-blog/making-an-stand-alone-executable-from-a-python-script-using-pyinstaller-d1df9170e263


if __name__ == "__main__":
    entry_point()
