import argparse
from pathlib import PosixPath
from typing import Callable
from logger import Logger
from file import File
from pathlib import Path

class Context:
    """ Shared context object"""
    logger: Logger
    cliargs: argparse.Namespace
    events: dict[str, list] = {}
    selected = {
        "path":"",
        "files":{},
        "regex":"movieyear"
    }
    regex: str = ""

    def on(self, event_name, event_fun):
        """ Register an event """
        if event_name not in self.events:
            self.events[event_name] = []

        self.events[event_name].append(event_fun)

    def emit(self, event_name, event_data:dict =None):
        """ Fire a registered event"""
        #self.logger.write_line(f"emit() called: {event}")
        if event_name in self.events:
            for func in self.events[event_name]:
                func(event_data)

    def set_selected_path(self, path: str):
        """ Set the selected path"""
        self.selected['path'] = path

    def add_selected_file(self, file:File):
        """ Add a selected file """
        if file.id not in self.selected['files']:
            self.selected['files'][file.id] = file

    def remove_selected_file(self, file:File):
        """ Remove a selected file """
        del self.selected['files'][file.id]

    def debug_selected_files(self):
        for fid, file in self.selected['files'].items():
            self.logger.write_line(f"selected file: {file.path.name}\n")

    def clear_selected_files(self):
        self.selected['files'] = {}

    def set_selected_regex(self, regex: str):
        self.selected['regex'] = regex


