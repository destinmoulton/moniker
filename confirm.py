import os
from pathlib import Path

from textual import events
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Label, Button, Input, RadioSet, RadioButton, Checkbox

from context import Context, MediaType

class Confirm(Vertical):
    ctx: Context

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.destination = ""
        self.ctx.on("confirm:doit", self.__perform_file_actions)

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-top-container"):
            with Vertical():
                yield Label("Destination Path")
                yield Input(id="confirm-path",
                            value="",
                            disabled=True)
            yield VerticalScroll(id="confirm-source-files")
            yield VerticalScroll(id="confirm-destination-files")

        yield ConfirmButtonBar(id="confirm-button-bar", ctx=self.ctx)

    def _on_show(self, event: events.Show) -> None:
        self.update_destination_path()
        self.update_fields()
        self.update_list_source_files()
        self.update_list_destination_files()

    def update_fields(self):
        input_path = self.query_one("#confirm-path")
        input_path.value = self.destination

    def update_destination_path(self):
        base = ""
        dir = ""
        suffix = ""
        subdir = ""
        if self.ctx.selected['mediatype']==MediaType.MOVIE:
            base = self.ctx.config.get("paths", "movies")
            suffix = self.ctx.parsed["year"]
        elif self.ctx.selected['mediatype']==MediaType.SHOW:
            base = self.ctx.config.get("paths", "shows")
            subdir = self.ctx.parsed["season"]

        dir = f"{self.ctx.parsed["title"]}"
        if suffix != "":
            dir = f"{dir}.{suffix}"

        if subdir != "":
            self.destination = os.path.join(base, dir, subdir)
        else:
            self.destination = os.path.join(base, dir)

    def update_list_source_files(self):
        container = self.query_one("#confirm-source-files")
        for fid, file in self.ctx.selected["files"].items():
            label = Label(str(file.path))
            container.mount(label)

    def update_list_destination_files(self):
        container = self.query_one("#confirm-destination-files")
        for fid, file in self.ctx.selected["files"].items():
            filename = self.ctx.final['filenames'][fid]
            fullpath = os.path.join(self.destination, filename)
            label = Label(str(fullpath))
            container.mount(label)

    def __perform_file_actions(self, event):
        if not os.path.exists(self.destination):
            os.makedirs(self.destination)

        for fid, file in self.ctx.selected["files"].items():
            srcpath = str(file.path)
            newfilename = self.ctx.final['filenames'][fid]
            destpath = os.path.join(self.destination, newfilename)
            os.rename(srcpath, destpath)
            if os.path.exists(destpath):
                self.ctx.logger.write_line(f"SUCCESS: moved {srcpath} to {destpath}")
            else:
                self.ctx.logger.write_line(f"ERROR: failed to move {srcpath} to {destpath}")



class ConfirmButtonBar(Horizontal):
    ctx: Context

    def __init__(self, id, ctx):
        super().__init__(id=id)
        self.ctx = ctx

    def compose(self) -> ComposeResult:
        yield Button(label="Back", id="confirm-button-back")
        yield Button(label="Do It!", id="confirm-button-doit", variant="success")

    def on_button_pressed(self, event: Button.Pressed)->None:
        if event.button.id == "confirm-button-back":
            params = {"screen":"parser"}
            self.ctx.emit("screen:change", params)
        elif event.button.id =="confirm-button-doit":
            params = {"screen":"browser"}
            self.ctx.emit("confirm:doit", {})
            self.ctx.emit("screen:change", params)
