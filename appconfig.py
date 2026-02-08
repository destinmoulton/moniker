import os
from pathlib import Path
from configparser import ConfigParser

class AppConfig:
    def __init__(self):
        self.filename = "config.ini"
        self.cfgparser = ConfigParser()
        self.fullpath = self.get_full_config_path()
        self.load()

    def load(self):
        if not self.does_config_file_exist():
            self.create_default_config()
        self.cfgparser.read(self.fullpath)

    def is_configured(self)->bool:
        if self.cfgparser["paths"]["movies"] == "":
            return False
        if self.cfgparser["paths"]["shows"] == "":
            return False
        return True

    def create_default_config(self):
        self.cfgparser.read(self.fullpath)
        self.cfgparser.add_section("paths")
        self.cfgparser.set('paths', 'movies', '')
        self.cfgparser.set('paths', 'shows', '')
        self.save()

    def get(self, section, setting):
        return self.cfgparser[section][setting]

    def set(self, section, setting, value):
        self.cfgparser.set(section, setting, value)

    def save(self):
        with open(self.fullpath, 'w') as f:
            self.cfgparser.write(f)

    def does_config_file_exist(self)->bool:
        configfile = Path(self.get_full_config_path())
        return configfile.exists()

    def get_full_config_path(self):
        _home = os.path.expanduser('~')

        xdgpath = os.environ.get('XDG_CONFIG_HOME') or \
                    os.path.join(_home, '.config')

        return os.path.join(xdgpath, self.filename)