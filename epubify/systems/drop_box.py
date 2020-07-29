import dropbox
import json
from uuid import uuid4
from os import remove
from epubify.utils.utils import read_json


class Dropbox(object):
    def __init__(self, **kwargs):
        self.cred_filename = "epubify/systems/vault/" + kwargs.get(
            "credsFileName", "api_keys.json"
        )
        self.token = read_json(file_path=self.cred_filename, key_name="dropbox").get(
            "token"
        )
        self.dropbox_client = dropbox.Dropbox(oauth2_access_token=self.token)
        account_names = (
            self.dropbox_client.users_get_current_account().name.given_name
            + " "
            + self.dropbox_client.users_get_current_account().name.surname
        )
        print("\t>> Connected to the dropbox account of", account_names)
        if "filePath" not in kwargs["to"].keys():
            self.output_file_path = "/%s.epub" % kwargs["article"].get(
                "title"
            )  # if no filePath, save to root
        else:
            self.output_file_path = "{given_path}/{book_title}.epub".format(
                given_path=kwargs["to"].get("filePath"),
                book_title=kwargs["article"].get("title"),
            )  # if no filePath, save to root

        self.save_mode = kwargs.get(
            "saveMode"
        )  # to overwrite the file if exists or not, default is NOT

    def save_book(self, book):
        mode = (
            dropbox.files.WriteMode.overwrite
            if self.save_mode == "overwrite"
            else dropbox.files.WriteMode.add
        )

        # Create temp file in order to be able to read bytes after that as this is what Dropbox requires to save it.
        tmp_path = "/tmp/{}.epub".format(uuid4())
        book.save(tmp_path)

        try:
            with open(tmp_path, "rb") as file:
                self.dropbox_client.files_upload(
                    f=file.read(), path=self.output_file_path, mode=mode, mute=True
                )
                print(
                    "\t>> File [SAVED] to Dropbox location: [{}]".format(
                        self.output_file_path, self.output_file_path
                    )
                )
                remove(tmp_path)  # Delete the temp file
        except TypeError as err:
            raise TypeError(
                "Expecting bytes data as input for the upload on dropbox. >> ERR >> %s"
                % err
            )
        except Exception as err:
            raise Exception(
                "There was a problem uploading file %s to Dropbox. >> ERR >> %s"
                % (self.output_file_path, err)
            )
