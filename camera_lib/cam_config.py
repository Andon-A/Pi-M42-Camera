import configparser
import os

cfg = configparser.ConfigParser()
cfg_path = "./config/config.cfg"
cfg.read(cfg_path)


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
    with open(cfg_path, 'w') as cfgfile:
        cfg.write(cfgfile)