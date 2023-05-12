# This file will download new updates from the specified location.

import os
import requests
import filecmp
import configparser

# Our file checker. Returns true if the file is "real" and false if it isn't.
def isDownloadable(header):
    if header.status_code != 200: # We only want full files.
        return False
    elif 'Content-Length' not in header.headers: # No Content
        return False
    else:
        return True # There's not a lot of tests here.
    

# Our downloader. It downloads the target file and checks to see if we can save it in the right spot.
def downloadFile(fileURL, target, overwrite=True):
    url = fileURL
    h = requests.head(url)
    if not isDownloadable(h):
        print("Target {0} not downloadable.".format(url))
        return False
    f = requests.get(url, allow_redirects=True)
    open("temp.py", 'wb').write(f)
    if not os.path.isfile(target):
        print("Saving {0}...".format(target))
        os.rename("temp.py", target)
        return True
    elif os.path.isfile(target) and not overwrite:
        print("Skipping {0}, file already exists and overwrite is off.".format(target))
        os.remove("temp.py")
        return False
    elif os.path.isfile(target) and filecmp.cmp(target, "temp.py"):
        print("Skipping {0}, same file already exists.".format(target))
        os.remove("temp.py")
        return False
    elif os.path.isfile(target) and not filecmp.cmp(target, "temp.py") and overwrite:
        print("Replacing {0} with remote version.".format(target))
        os.remove(target)
        os.rename("temp.py", target)
        return True
    else:
        print("Unknown error with {0}. Aborting file.".format(target))
        return False

# Load our config file.
config = configparser.ConfigParser(allow_no_value=True)
config.read("./config/updater.cfg")

# Then download the new config file.
print("Downloading update list...")
dl = downloadFile(config["INFO"]["ConfigURL"], "/config/updater.cfg")

if dl:
    print("Update list downloaded.")
    # We have downloaded our file, so reload it.
    config = configparser.ConfigParser(allow_no_value=True)
    config.read("./config/updater.cfg")
    url_base = config["INFO"]["MainURL"]
    # Now download our files.
    for file in config["Files"]:
        url = url_base + file
        print("Downloading {0}".format(url))
        target = "./" + file
        downloadFile(url, target)

else:
    print("Update list download failed. Aborting.")
    exit()