import os
from pathlib import Path
from typing import Iterable

from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, VerticalScroll, Vertical
from textual.screen import Screen
from textual.widgets import Placeholder, DirectoryTree, Log, Checkbox

MEDIA_FILE_EXTENSIONS = ["mp4", "avi", "mkv"]

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
        width: 1fr;
        margin: 0 2;
    }
    """

    def __init__(self, logger):
        super().__init__()
        self.logger = logger

    def compose(self) -> ComposeResult:
        yield FilteredDirectoryTree("./")


class FileSelector(VerticalScroll):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger

    def update_files(self, directory: Path):
        # remove existing checkboxes
        self.query(Checkbox).remove()

        if directory.is_dir():
            for file_path in sorted(directory.iterdir()):
                if file_path.is_file():
                    checkbox = Checkbox(file_path.name)
                    checkbox.data = file_path
                    checkbox.value = self.should_select_file(file_path)
                    self.mount(checkbox)

    def should_select_file(self, file_path: Path)->bool:

        filename, file_extension = os.path.splitext(file_path)

        if file_extension in MEDIA_FILE_EXTENSIONS:
            return True

        return False






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

    DEFAULT_CSS = """
    Column {
        height: 1fr;
        width: 1fr;
        margin: 0 2;
    }
    """
    def __init__(self, logger):
        super().__init__()
        self.logger = logger

    def compose(self) -> ComposeResult:
        yield DirectoryBrowser(self.logger)
        yield self.logger

class MiddleColumn(Vertical):
    DEFAULT_CSS = """
    Column {
        height: 1fr;
        width: 1fr;
        margin: 0 2;
    }
    """
    def __init__(self, logger):
        super().__init__()
        self.logger = logger

    def compose(self) -> ComposeResult:
        yield FileSelector(self.logger)


class MonikerScreen(Screen):
    def __init__(self):
        super().__init__()
        self.logger = Logger()

    def compose(self) -> ComposeResult:
        yield Header(id="Header")
        yield Footer(id="Footer")
        with HorizontalScroll():
            yield LeftColumn(self.logger)
            yield MiddleColumn(self.logger)

    def on_directory_tree_directory_selected(self, event:  DirectoryTree.DirectorySelected) -> None:
        path = event.path
        self.logger.write_line(f"Listing: {path}")

        file_selector = self.query_one(FileSelector)
        file_selector.update_files(event.path)

class LayoutApp(App):
    def on_ready(self) -> None:
        self.push_screen(MonikerScreen())

if __name__ == "__main__":
    app = LayoutApp()
    app.run()