import configparser
import os

cfg = configparser.ConfigParser()
cfg_path = "./config/config.cfg"
cfg_backup = "./config/config.backup"
cfg.read(cfg_path)

# If we don't have anything, try the backup.
if "Settings" not in cfg:
    cfg.read(cfg_backup)

# And, if we somehow still don't have things...

if "Settings" not in cfg:
    # We need our default settings.
    cfg["Settings"] = {}
    cfg["Settings"]["JPEG"] = "True"
    cfg["Settings"]["DNG"] = "True"
    cfg["Settings"]["Mode"] = "0"
    cfg["Settings"]["Exposure"] = "0.0"
    cfg["Settings"]["ISO"] = "0"
if "Info" not in cfg:
    cfg["Info"] = {}
    cfg["Info"]["NextImg"] = "0000"
    cfg["Info"]["NextVid"] = "0000"
    cfg["Info"]["ImgPath"] = "/photos/default/Images"
    cfg["Info"]["VidPath"] = "/photos/default/Videos"

def save_config():
    # Deletes the old backup, saves our current as the backup, then saves the new version.
    if os.path.isfile(cfg_backup):
        os.remove(cfg_backup)
    os.rename(cfg_path, cfg_backup)
    with open(cfg_path, 'w') as cfgfile:
        cfg.write(cfgfile)