from pathlib import Path
from typing import Iterable

from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, VerticalScroll, Vertical
from textual.screen import Screen
from textual.widgets import Placeholder, DirectoryTree, Log


class Header(Placeholder):
    DEFAULT_CSS = """
    Header {
        height: 3;
        dock: top;
    }
    """


class Footer(Placeholder):
    DEFAULT_CSS = """
    Footer {
        height: 3;
        dock: bottom;
    }
    """

class FilteredDirectoryTree(DirectoryTree):
    # Filter to show just the folders
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if path.is_dir()]

    def on_directory_tree_directory_selected(self, directory_tree: DirectoryTree) -> None:
        return None

class DirectoryBrowser(VerticalScroll):
    DEFAULT_CSS = """
    Column {
        height: 0.7fr;
        width: 0.5fr;
        margin: 0 2;
    }
    """

    def __init__(self, logger):
        super().__init__()
        self.logger = logger

    def compose(self) -> ComposeResult:
        yield FilteredDirectoryTree("./")


class Logger(Log):
    DEFAULT_CSS = """
    Column {
        height: 0.3fr;
        width: 0.5fr;
        margin: 0 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Log()

    def on_ready(self) -> None:
        #log = self.query_one(Log)
        self.write_line("Hello, World!")


class LeftColumn(Vertical):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger

    def compose(self) -> ComposeResult:
        yield DirectoryBrowser(self.logger)
        yield self.logger


class MonikerScreen(Screen):
    def __init__(self):
        super().__init__()
        self.logger = Logger()

    def compose(self) -> ComposeResult:
        yield Header(id="Header")
        yield Footer(id="Footer")
        with HorizontalScroll():
            yield LeftColumn(self.logger)

class LayoutApp(App):
    def on_ready(self) -> None:
        self.push_screen(MonikerScreen())

if __name__ == "__main__":
    app = LayoutApp()
    app.run()