from context import Context
from textual.containers import Horizontal
from textual.app import ComposeResult
from textual.widgets import Label, Button

class Renamer(Horizontal):
    ctx: Context

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    def compose(self) -> ComposeResult:
        yield Label("test")
        yield RenamerButtonBar(id="renamer-button-bar", ctx=self.ctx)

class RenamerButtonBar(Horizontal):
    ctx: Context

    def __init__(self, id, ctx):
        super().__init__(id=id)
        self.ctx = ctx

    def compose(self) -> ComposeResult:
        yield Button(label="Back", id="renamer-button-back")


    def on_button_pressed(self, event: Button.Pressed)->None:
        if event.button.id == "renamer-button-back":
            params = {"screen":"browser"}
            self.ctx.emit("screen:change", params)

