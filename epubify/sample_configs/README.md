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
- `to`.`author` - if no author is provided, the default value `epubify` will be assigned as author.
- `to`.`system` - required only when the __`mode`__ is set to __`remote`__. The options that can be assigned to it are:
    - `dropbox` - save to dropbox (__currently in development__)
    - more coming soon