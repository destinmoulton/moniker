import os
from configparser import ConfigParser

class AppConfig:
    def __init__(self):
        self.filename = "config.ini"
        self.config = ConfigParser()
        self.fullpath = self.get_full_config_path()

    def create_default_config(self):
        self.config.read(self.fullpath)
        self.config.add_section("paths")
        self.config.set('paths', 'movies', '')
        self.config.set('paths', 'shows', '')
        self.save()

    def save(self):
        with open(self.fullpath, 'w') as f:
            self.config.write(f)

    def get_full_config_path(self):
        _home = os.path.expanduser('~')

        xdgpath = os.environ.get('XDG_CONFIG_HOME') or \
                    os.path.join(_home, '.config')

        return os.path.join(xdgpath, self.filename)