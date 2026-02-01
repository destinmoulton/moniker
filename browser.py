
import os
from pathlib import Path, PosixPath
from typing import Iterable
from context import Context
from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, VerticalScroll, Vertical, Horizontal
from textual.containers import HorizontalScroll, VerticalScroll, Vertical, Horizontal
from textual.widgets import Placeholder, DirectoryTree, Log, Checkbox, Button

MEDIA_FILE_EXTENSIONS = ["mp4", "avi", "mkv"]

class Browser(Horizontal):
    ctx: Context

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    def compose(self)->ComposeResult:
        yield LeftColumn(self.ctx)
        yield RightColumn(self.ctx)


class FilteredDirectoryTree(DirectoryTree):
    ctx: Context

    def __init__(self, ctx):
        super().__init__(ctx.cliargs.directory)
        self.ctx = ctx

    # Filter to show just the folders
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if path.is_dir()]

    def on_directory_tree_directory_selected(self, event:  DirectoryTree.DirectorySelected):
        path = event.path
        self.ctx.emit("browser:directory-changed", {'path': path})
        self.ctx.logger.write_line(f"Listing: {path}")


class DirectoryBrowser(VerticalScroll):
    ctx: Context

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    def compose(self) -> ComposeResult:
        yield FilteredDirectoryTree(self.ctx)


class FileSelector(VerticalScroll):
    ctx: Context

    def __init__(self, id, ctx):
        super().__init__(id=id)
        self.ctx = ctx
        self.ctx.on("browser:directory-changed", self.__directory_changed);

    def __directory_changed(self, event) -> None:
        path: PosixPath = event['path']
        self.update_files(path)

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
    ctx: Context

    def __init__(self, id, ctx):
        super().__init__(id=id)
        self.ctx = ctx

    def compose(self) -> ComposeResult:
        yield Button("Movie")


class LeftColumn(Vertical):
    ctx: Context

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    def compose(self) -> ComposeResult:
        yield DirectoryBrowser(self.ctx)


class RightColumn(Vertical):
    ctx: Context

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.file_selector = FileSelector(id="file-selector-container", ctx=self.ctx)

    def compose(self) -> ComposeResult:
        yield self.file_selector
        yield FileSelectorButtonBar(id="file-selector-buttonbar", ctx=self.ctx)

    def on_directory_tree_directory_selected(self, event:  DirectoryTree.DirectorySelected) -> None:
        path = event.path
        self.ctx.logger.write_line(f"Listing: {path}")

        self.file_selector.update_files(event.path)
