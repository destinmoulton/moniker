from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Label, Button, Input, RadioSet, RadioButton, Checkbox

from context import Context, MediaType

class Destination(Vertical):
    ctx: Context

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    def compose(self) -> ComposeResult:
        # with Horizontal(id="destination-top-container"):
        #     yield MoverLeftColumn(id="mover-left-column", ctx=self.ctx)
        #     with Vertical(id="mover-right-column"):
        #         yield MoverFileFields(id="mover-file-fields-container", ctx=self.ctx)
        with Horizontal(id="destination-top-container"):
            yield Label("test")
        yield DestinationButtonBar(id="destination-button-bar", ctx=self.ctx)


class DestinationButtonBar(Horizontal):
    ctx: Context

    def __init__(self, id, ctx):
        super().__init__(id=id)
        self.ctx = ctx

    def compose(self) -> ComposeResult:
        yield Button(label="Back", id="destination-button-back")
        yield Button(label="Next", id="destination-button-next", variant="success")

    def on_button_pressed(self, event: Button.Pressed)->None:
        if event.button.id == "destination-button-back":
            params = {"screen":"mover"}
            self.ctx.emit("screen:change", params)
        elif event.button.id =="destination-button-next":
            params = {"screen":"preview"}
            self.ctx.emit("screen:change", params)
