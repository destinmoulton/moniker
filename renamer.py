from textual import events

from context import Context
from textual.containers import Container, Horizontal, Vertical, VerticalScroll

from textual.app import ComposeResult
from textual.widgets import Label, Button, Input

class Renamer(Vertical):
    ctx: Context

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    def compose(self) -> ComposeResult:
        with Horizontal(id="renamer-top-container"):
            yield RenamerLeftColumn(id="renamer-left-column", ctx=self.ctx)
            with Vertical(id="renamer-right-column"):
                yield RenamerFileFields(id="renamer-file-fields-container", ctx=self.ctx)

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

class RenamerLeftColumn(VerticalScroll):
    ctx: Context
    def __init__(self, id, ctx):
        super().__init__(id=id)
        self.ctx = ctx

    def compose(self) -> ComposeResult:
        yield Label("Identifier Regex")
        yield Input(id="renamer-input-regex", classes="renamer-input", value="S01E01")

class RenamerFileFields(VerticalScroll):
    ctx: Context
    def __init__(self, id, ctx):
        super().__init__(id=id)
        self.ctx = ctx

    def on_show(self) -> None:
        self.__build_fields()

    def __build_fields(self)->None:
        # Clear the verticals from the container
        self.query(Vertical).remove()

        self.ctx.debug_selected_files()
        for fid, file in self.ctx.selected["files"].items():
            fieldgroup = Vertical(classes="renamer-file-fieldgroup")
            self.mount(fieldgroup)

            fieldgroup.mount(Label(file.path.name))
            fieldgroup.mount(Input(id=f"renamer-file-{fid}", classes="renamer-input", value=file.path.name))
            self.ctx.logger.write_line(f"{fid}: {file.path}")

        self.refresh(layout=True)
