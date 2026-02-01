from textual.app import ComposeResult

from textual.widgets import Log

class Logger(Log):

    def compose(self) -> ComposeResult:
        yield Log()

    def on_ready(self) -> None:
        #log = self.query_one(Log)
        self.write_line("Hello, World!")
