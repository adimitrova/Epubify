<img src="img/epubify.png" alt="drawing" width="300"/>

![status](https://img.shields.io/badge/status-active%20development-yellow)
![release](https://img.shields.io/badge/release-v0.1%20beta-green)
![Black Logo](https://img.shields.io/badge/code%20style-black-000000.svg)

# ePubify

Have you ever wanted to read that huge article, but in a more readable format AND on your EBOOK reader? Maybe you started reading it, but didn't have time to finish? Maybe you use the Pocket application to save your articles? BUT that's not the same like your favourite Kindle or Pocketbook device?! Your eyes hurt?

ePubify is the answer to all that - it's a small application that will fetch the text from your article by having the URL and will store the output epub file directly on your dropbox. If you dropbox contains the folder which your Pocketbook or Kindle syncs from, that means you automatically get that long and interesting article ready for you to sync down on your device and read on your way to work! :) 

Enjoy!

### Architecture
------------

<img src="img/epubify_diagram.jpg" alt="drawing" width="1000"/>

### Installation
------------

```shell
git clone git://github.com/adimitrova/coding_projects.git
cd Python/epubify
pip install -r requirements.txt
```

--------

## Reading articles

#### Pocket app
Once you run ePubify, it will use epubify's code to request user access code, it will then request the user to authorize the application by automatically opening the browser. Please accept, if you agree to the term. ePubify will request __full access__. But the only thing it actually does, is read your article list, fetch their original URLs and process them. 

To start the application, create your json config file, copy the path to it and run as follows:

```shell
python3 main.py --cf '/path/to/config.json'
```

__NB!__ Sample config available: `sample_configs/pocket_articles_to_dropbox.json`

--------

## Saving ebooks

#### Local machine
You can save to local machine by providing the path to a directory where you want to get your books in the end of the processing. You can pass this in the json config, or via CLI with the `-fp` argument. If this argument is skipped, files will be saved to your Desktop.


#### Dropbox
(coming soon)