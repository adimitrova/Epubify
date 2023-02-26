# Key-value pairs for configs, explained
All configs will have 2 main top-level keys with mandatory sub-keys as follows:

```json
{
    "from": {
        "system": "pocket|txt|url"
    },
    "to": {
        "mode": "local|remote",
        "system": "dropbox|local"
    },
}
```

If there are multiple articles the user would like to convert, a key, called `articles` must be present:
```json
{
    "from": {
        "system": "pocket|txt|url"
    },
    "to": {
        "mode": "local|remote",
        "system": "dropbox|{more_coming_soon}"
    },
    "articles": {}
}
```

Following, we have the system to system specific keys.

## General notes for all systems

__MANDATORY KEYS__: every dot means one level deeper

- `from`.`system` - always required in order for Epubify to process the data
- `to`.`mode` - this is a mandatory key in order for the application to decide how to do the processing of the book.
This is also because if you have dropbox synced locally on your computer, you may still say local and have the application
saved to a path that leads to your local dropbox synced folder where your eBook reader is syncing from.
For example I have the following path: `/home/{user_id}/dropbox/apps/Dropbox PocketBook/articles/` location.
In this case, my mode will be set to "local" and `to`.`system` will be completely skipped from the config.
See `pocket_to_local.json` config.

__OPTIONAL KEYS__: every dot means one level deeper
- `to`.`filePath` can be added if you wish to save the epub files to a location,
different than the default `epubify/books/` folder. The path should be a full path, for example `/home/{userid}/Desktop/books/`
and should be an already existing directory. We currently __do not create__ the directory if it doesn't exist and the
processing will fail. This will be fixed soon.

__NB!__ The path must _NOT_ have a slash at the end, e.g. `path/to/directory` instead of `path/to/directory/` and must _NOT_ include a filename, only the _directory_ where the files will be saved.
- `to`.`author` - if no author is provided, the default value `epubify` will be assigned as author.
- `to`.`system` - required only when the __`mode`__ is set to __`remote`__. The options that can be assigned to it are:
    - `dropbox` - save to dropbox (__currently in development__)
    - more coming soon
- `saveMode` - add this option inside the `to` block to tell Dropbox to save in mode either `overwrite` or `append`
- `credsFileName`: When the target system is `dropbox`, then this key will serve to give the path to the credentials file for dropbox. You can skip this key, if you create a file called 'api_keys.json' and make it look like below, put the file in `epubify/systems/vault/` directory and it will be fine.

```json
{
    "dropbox": {
        "token": "xxxxxxx",
        "app_key": "xxxxxxx",
        "app_secret": "xxxxxxx"
    }
}
```

To generate your key, go to you [App Console](https://www.dropbox.com/developers/apps/create) and follow the instructions:
```text
Click "Create app":
1. Choose an API: "Dropbox API"
2. Choose the type of access you need
    a) App folder: Select this if you want Epubify to access only a specific folder in your dropbox
    b) Full Dropbox: Epubify will be able to save anywhere on your dropbox
3. Name your app: "epubify"
```

--------

### Dropbox full config incl. optional keys

```json
{
    "from": {
        "system": "pocket"
    },
    "to": {
        "mode": "remote",
        "filePath": "/Apps/Pocketbook/articles",
        "system": "dropbox",
        "saveMode": "overwrite"
    },
    "credsFileName": "my_keys.json"
}
```
