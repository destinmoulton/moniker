import argparse
from pathlib import PosixPath
from typing import Callable
from logger import Logger
class Context:
    """ Shared context object"""
    logger: Logger
    cliargs: argparse.Namespace
    events: dict[str, list] = {}
    selected = {
        "path":"",
        "files":set()
    }

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

    def add_selected_file(self, path:str):
        """ Add a selected file """
        self.selected['files'].add(path)

    def remove_selected_file(self, path):
        """ Remove a selected file """
        self.selected['files'].remove(path)

    def clear_selected_files(self):
        self.selected['files'] = set()

