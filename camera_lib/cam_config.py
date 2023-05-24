import configparser

cfg = configparser.ConfigParser()
cfg_path = "../config/config.cfg"
cfg.read(cfg_path)

def save_config():
    with open(cfg_path, 'w') as cfgfile:
        config.write(cfgfile)