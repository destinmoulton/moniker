
import os
from pathlib import Path, PosixPath
from typing import Iterable
from context import Context
from textual.app import ComposeResult
from textual.containers import HorizontalScroll, VerticalScroll, Vertical, Horizontal
from textual.containers import HorizontalScroll, VerticalScroll, Vertical, Horizontal
from textual.widgets import Placeholder, DirectoryTree, Log, Checkbox, Button

MEDIA_FILE_EXTENSIONS = ["mp4", "avi", "mkv", "m4v", "srt"]

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
        self.ctx.set_selected_path(str(path))
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
        self.ctx.clear_selected_files()
        self.update_files_list(path)

    def update_files_list(self, directory: Path):
        # remove existing checkboxes
        self.query(Checkbox).remove()

        if directory.is_dir():
            for file_path in sorted(directory.iterdir()):
                if file_path.is_file():
                    checkbox = Checkbox(label=file_path.name, classes="file-selector-checkbox")
                    checkbox.data = str(file_path.name)
                    checkbox.value = self.should_preselect_file(file_path)
                    self.mount(checkbox)

    def on_checkbox_changed(self, event) -> None:
        if event.value is True:
            self.ctx.add_selected_file(event.checkbox.data)
        else:
            self.ctx.remove_selected_file(event.checkbox.data)

    def should_preselect_file(self, file_path: Path)->bool:

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
        yield Button(label="Rename Movie", id="rename-movie")

    def on_button_pressed(self, event: Button.Pressed)->None:
        self.ctx.logger.write_line(f"button pressed {event.button.id}")

        type="show"
        if event.button.id == "rename-movie":
            type = "movie"
        params = {"screen":"renamer", "type":type}
        self.ctx.emit("screen:change", params)


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
