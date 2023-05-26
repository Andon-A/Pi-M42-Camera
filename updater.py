# This file will download new updates from the specified location.

import os
import requests
import filecmp
import configparser
import socket

fallback_cfg = "https://raw.githubusercontent.com/Andon-A/Pi-M42-Camera/main/camera_lib/config/updater.cfg"

# Check if we're connected to the internet.
def isConnected():
    print("Checking internet connection.")
    try:
        # Is our file server actually reachable?
        sock = socket.create_connection(("raw.githubusercontent.com", 80))
        if sock is not None:
            print("Internet connected")
            sock.close
        return True
    except OSError:
        pass
    print("Internet unavailable, update aborted.")
    return False

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
    open("temp.py", 'wb').write(f.content)
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
        return True # We didn't download it, but it's the same file.
    elif os.path.isfile(target) and not filecmp.cmp(target, "temp.py") and overwrite:
        print("Replacing {0} with remote version.".format(target))
        os.remove(target)
        os.rename("temp.py", target)
        return True
    else:
        print("Unknown error with {0}. Aborting file.".format(target))
        return False

def update(overwrite=True):
    
    # Check our internet connection before continuing.
    if not isConnected():
        return False

    dl = False
    # Load our config file.
    if os.path.isfile("./camera_lib/config/updater.cfg"):
        print("Loading config file...")
        config = configparser.ConfigParser(allow_no_value=True)
        config.read("./camera_lib/config/updater.cfg")
        # And try to download the new one.
        print("Downloading update list...")
        dl = downloadFile(config["INFO"]["ConfigURL"], "./camera_lib/config/updater.cfg", overwrite)
    # We don't have a config file, so download one.
    else:
        print("Config file not found. Downloading fallback...")
        if not os.path.isdir("./camera_lib"):
            os.mkdir("camera_lib")
        if not os.path.isdir("./camera_lib/config"):
            os.mkdir("camera_lib/config")
        print("Downloading update list...")
        dl = downloadFile(fallback_cfg, "./camera_lib/config/updater.cfg", overwrite)

    if dl:
        print("Update list downloaded.")
        # We have downloaded our file, so reload it.
        config = configparser.ConfigParser(allow_no_value=True)
        config.read("./camera_lib/config/updater.cfg")
        url_base = config["INFO"]["MainURL"]
        # Make our folders
        for folder in config["Folders"]:
            if not os.path.isdir("./" + folder):
                os.makedirs("./" + folder)
        # Now download our files.
        for file in config["Files"]:
            url = url_base + file
            print("Downloading {0}".format(file[file.rfind("/")+1:]))
            target = "./" + file
            overwrite = config["Files"].getboolean(file)
            downloadFile(url, target, overwrite)
        print("Update complete.")
        return True

    else:
        print("Update list download failed. Aborting.")
        return False