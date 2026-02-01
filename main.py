import argparse
import os
import styles
from browser import Browser
from logger import Logger
from pathlib import Path
from typing import Iterable

from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, VerticalScroll, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Placeholder, DirectoryTree, Log, Checkbox, Button

MEDIA_FILE_EXTENSIONS = ["mp4", "avi", "mkv"]

class Header(Placeholder):
    DEFAULT_CSS = """
    Header {
        height: 1;
        dock: top;
    }
    """



class FilteredDirectoryTree(DirectoryTree):
    # Filter to show just the folders
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if path.is_dir()]

    def on_directory_tree_directory_selected(self, directory_tree: DirectoryTree) -> None:
        return None

class DirectoryBrowser(VerticalScroll):

    def __init__(self, logger, cliargs):
        super().__init__()
        self.logger = logger
        self.cliargs = cliargs

    def compose(self) -> ComposeResult:
        yield FilteredDirectoryTree(self.cliargs.directory)


class FileSelector(VerticalScroll):
    def __init__(self, id, logger):
        super().__init__(id=id)
        self.logger = logger

    def update_files(self, directory: Path):
        # remove existing checkboxes
        self.query(Checkbox).remove()

        if directory.is_dir():
            for file_path in sorted(directory.iterdir()):
                if file_path.is_file():
                    checkbox = Checkbox(label=file_path.name, classes="file-selector-checkbox")
                    checkbox.data = file_path
                    checkbox.value = self.should_select_file(file_path)
                    self.mount(checkbox)

    def should_select_file(self, file_path: Path)->bool:

        filename, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()
        file_extension = file_extension[1:]

        if file_extension in MEDIA_FILE_EXTENSIONS:
            return True

        return False

class FileSelectorButtonBar(Horizontal):
    def __init__(self, id, logger):
        super().__init__(id=id)
        self.logger = logger
    def compose(self) -> ComposeResult:
        yield Button("Movie")





class LeftColumn(Vertical):

    def __init__(self, logger, cliargs):
        super().__init__()
        self.logger = logger
        self.cliargs = cliargs

    def compose(self) -> ComposeResult:
        yield DirectoryBrowser(self.logger, self.cliargs)

class MiddleColumn(Vertical):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger

    def compose(self) -> ComposeResult:
        yield FileSelector(id="file-selector-container", logger=self.logger)
        yield FileSelectorButtonBar(id="file-selector-buttonbar", logger=self.logger)


class MonikerScreen(Screen):
    def __init__(self, cliargs):
        super().__init__()
        self.logger = Logger()
        self.cliargs = cliargs

    def compose(self) -> ComposeResult:
        yield Header(id="Header")
        with HorizontalScroll():
            yield LeftColumn(self.logger, self.cliargs)
            yield MiddleColumn(self.logger)

        yield self.logger

    def on_directory_tree_directory_selected(self, event:  DirectoryTree.DirectorySelected) -> None:
        path = event.path
        self.logger.write_line(f"Listing: {path}")

        file_selector = self.query_one(FileSelector)
        file_selector.update_files(event.path)

class LayoutApp(App):
    CSS = styles.CSS
    def __init__(self, cliargs):
        super().__init__()
        self.cliargs = cliargs

    def on_ready(self) -> None:
        self.push_screen(MonikerScreen(self.cliargs))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="moniker", description="moniker moves and renames files")
    parser.add_argument("directory", default=".", help="starting directory")
    cliargs = parser.parse_args()

    app = LayoutApp(cliargs=cliargs)
    app.run()