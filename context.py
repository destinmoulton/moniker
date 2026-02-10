import argparse
from enum import Enum
from pathlib import PosixPath
from typing import Callable
from logger import Logger
from file import File
from pathlib import Path
from appconfig import AppConfig

class MediaType(Enum):
    MOVIE = "movie"
    SHOW = "show"

class Context:
    """ Shared context object"""
    logger: Logger
    config: AppConfig
    cliargs: argparse.Namespace
    events: dict[str, list] = {}
    selected = {
        "path":"",
        "files":{},
        "mediatype":MediaType.MOVIE,
    }
    possible = {
        "season":"",
        "year":"",
        "nameparts":[]
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

    def reset_selected(self):
        self.selected['path'] = ""
        self.selected['files'] = {}
        self.selected['mediatype'] = MediaType.MOVIE

    def reset_possible(self):
        self.possible['season'] = ""
        self.possible['year'] = ""
        self.possible['nameparts'] = []

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

    def set_selected_mediatype(self, mediatype: MediaType):
        self.selected['mediatype'] = mediatype

    def set_possible_season(self, season: str):
        self.possible['season'] = season

    def set_possible_year(self, year: str):
        self.possible['year'] = year

    def set_possible_nameparts(self, name_parts: list):
        for prt in name_parts:
            if prt not in self.possible['nameparts']:
                self.possible['nameparts'].append(prt)

    def get_possible_name(self):
        return ".".join(self.possible['nameparts'])