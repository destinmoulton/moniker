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


    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Destination Path")
            yield Input(id="confirm-path",
                        value="",
                        disabled=True)
        yield VerticalScroll(id="confirm-source-files")
        yield VerticalScroll(id="confirm-final-files")

        yield ConfirmButtonBar(id="confirm-button-bar", ctx=self.ctx)

    def _on_show(self, event: events.Show) -> None:
        self.update_destination_path()
        self.update_fields()
        self.update_source_files()

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

    def update_source_files(self):
        container = self.query_one("#confirm-source-files")
        for fid, file in self.ctx.selected["files"].items():
            label = Label(str(file.path))
            container.mount(label)


class ConfirmButtonBar(Horizontal):
    ctx: Context

    def __init__(self, id, ctx):
        super().__init__(id=id)
        self.ctx = ctx

    def compose(self) -> ComposeResult:
        yield Button(label="Back", id="confirm-button-back")
        yield Button(label="Do It!", id="confirm-button-next", variant="success")

    def on_button_pressed(self, event: Button.Pressed)->None:
        if event.button.id == "confirm-button-back":
            params = {"screen":"mover"}
            self.ctx.emit("screen:change", params)
        elif event.button.id =="confirm-button-next":
            params = {"screen":"preview"}
            self.ctx.emit("screen:change", params)
