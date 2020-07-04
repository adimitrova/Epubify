import dropbox
import json


class Dropbox(object):
    def __init__(self, **kwargs):
        self.cred_filename = 'systems/vault/' + kwargs.get('credsFileName', "api_keys.json")
        self.token = self._fetch_token_from_cred_file(self.cred_filename)
        self.dropbox_client = dropbox.Dropbox(oauth2_access_token=self.token)
        account_names = self.dropbox_client.users_get_current_account().name.given_name + ' ' + self.dropbox_client.users_get_current_account().name.surname
        print("\t>> Connected to the dropbox account of", account_names)
        self.output_file_path = kwargs.get('filePath', '')      # if no filePath, save to root
        self.save_mode = kwargs.get('save_mode')    # to overwrite the file if exists or not, default is NOT

    def _fetch_token_from_cred_file(self, cred_filename):
        with open(cred_filename, 'r') as file:
            creds = json.load(file).get('dropbox')

        return creds['token']

    def save_book(self, book):
        dbx = dropbox.Dropbox(self.token)
        mode = (dropbox.files.WriteMode.overwrite if self.save_mode == 'overwrite' else dropbox.files.WriteMode.add)

        try:
                dbx.files_upload(f=book, path=self.output_file_path, mode=mode, mute=True)
                print("\t>> File [SAVED] to Dropbox location: [{}]".format(self.output_file_path, self.output_file_path))
        except TypeError:
            raise TypeError("Expecting bytes data as input for the upload on dropbox.")
        except Exception as err:
            raise Exception("There was a problem uploading file %s to Dropbox. Error: %s" % (self.output_file_path, err))