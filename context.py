import argparse
import re
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

MediaTypeRegex = {
    MediaType.SHOW: '[Ss](\\d+)[Ee](\\d+)',
    MediaType.MOVIE: '(19[0-9]{2}|2[0-9]{3})'
}

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
    guessed = {
        "title":"",
        "season":"",
        "year":"",
        "episodes":{}
    }
    regex = {
        "is_valid":True,
        "string":"",
        "pattern":re.Pattern
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

    def reset_all(self):
        self.reset_selected()
        self.reset_guessed()
        self.reset_final()

    def reset_selected(self):
        self.selected['path'] = ""
        self.selected['files'] = {}
        self.selected['mediatype'] = MediaType.MOVIE

    def reset_guessed(self):
        self.guessed['season'] = ""
        self.guessed['year'] = ""
        self.guessed['title'] = ""
        self.guessed['episodes'] = {}

    def reset_final(self):
        self.final['media_title'] = ""
        self.final['season'] = ""
        self.final['year'] = ""
        self.final['filenames'] = {}

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

    def set_guessed_title(self, title: str):
        self.guessed['title'] = title

    def set_guessed_season(self, season: str):
        self.guessed['season'] = season

    def set_guessed_year(self, year: str):
        self.guessed['year'] = year

    def set_guessed_episode(self, fid: str, episode: str):
        self.guessed['episodes'][fid] = episode
