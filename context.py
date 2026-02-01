import argparse
from typing import Callable
from logger import Logger
class Context:
    """ Shared context object"""
    logger: Logger
    cliargs: argparse.Namespace
    events: dict[str, Callable] = {}

    def on(self, event_name, event_fun):
        self.events[event_name] = event_fun

    def emit(self, event_name, event:dict =None):
        #self.logger.write_line(f"emit() called: {event}")
        if event_name in self.events:
            self.events[event_name](event)

