
import os
from pathlib import Path, PosixPath
from typing import Iterable

from textual.geometry import Region

from context import Context, MediaType
from file import File
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
    ICON_NODE = "🗀 "
    ICON_NODE_EXPANDED = "🗀 "

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
                    file = File(file_path)
                    is_mediafile = self.should_preselect_file(file_path)
                    classes = ["file-selector-checkbox"]
                    if is_mediafile:
                        classes.append("file-selector-checkbox-mediafile")
                    checkbox = Checkbox(label=file_path.name, classes=" ".join(classes))
                    checkbox.data = file
                    checkbox.value = is_mediafile
                    self.mount(checkbox)
                    if is_mediafile:
                        self.ctx.add_selected_file(file)

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
        self.visible = False
        self.ctx.on("browser:directory-changed", self.__directory_changed)

    def compose(self) -> ComposeResult:
        yield Button(label="Move Movie",
                     classes="browser-button-move",
                     variant="primary",
                     id="button-move-movie")
        yield Button(label="Move Show Episodes",
                     classes="browser-button-move",
                     variant="success",
                     id="button-move-show")

    def on_button_pressed(self, event: Button.Pressed)->None:

        type= MediaType.SHOW
        if event.button.id == "button-move-movie":
            type = MediaType.MOVIE
            self.ctx.set_selected_mediatype(MediaType.MOVIE)
        elif event.button.id == "button-move-show":
            type = MediaType.SHOW
            self.ctx.set_selected_mediatype(MediaType.SHOW)

        params = {"screen":"mover", "type":type}
        self.ctx.emit("screen:change", params)

    def __directory_changed(self, event: DirectoryTree.DirectorySelected) -> None:
        self.visible = True


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
