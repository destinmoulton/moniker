from textual.app import ComposeResult

from textual.widgets import Log

class Logger(Log):

    def __init__(self):
        super().__init__()
        self.__logwidg = Log()

    def compose(self) -> ComposeResult:
        yield self.__logwidg

    def on_ready(self) -> None:
        self.__logwidg.write_line("Hello, World!")
