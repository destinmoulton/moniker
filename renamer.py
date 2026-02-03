import re
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
    default_seasep_regex: str =  "[Ss](\d+)[Ee](\d+)"

    def __init__(self, id, ctx):
        super().__init__(id=id)
        self.ctx = ctx

    def compose(self) -> ComposeResult:
        yield Label("Identifier Regex")
        with Vertical():
            yield Input(id="renamer-input-regex", classes="renamer-input", value=self.default_seasep_regex)

    def on_input_changed(self, event):
        if event.input.id == "renamer-input-regex":
            self.ctx.regex = event.value
            self.ctx.emit("renamer:regex:changed", {"value": event.value})


class RenamerFileFields(VerticalScroll):
    ctx: Context
    def __init__(self, id, ctx):
        super().__init__(id=id)
        self.ctx = ctx
        self.ctx.on("renamer:regex:changed", self.__regex_changed)

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
        self.update_file_fields()

    def __regex_changed(self, event)->None:
        self.update_file_fields()

    def update_file_fields(self)->None:
        regex = re.compile(self.ctx.regex)
        for fid, file in self.ctx.selected["files"].items():
            finput = self.query_one(f"#renamer-file-{fid}")
            fparts = file.parts.copy()

            replacement_string = ""
            replacement_idx = 0
            found = False
            for pidx, part in enumerate(fparts):
                match = regex.search(part)

                if match:
                    found = True

                    seasnum = int(match.group(1))
                    epnum = int(match.group(2))
                    season = str(seasnum)
                    if(seasnum<10):
                        season = "0" + season
                    episode = str(epnum)
                    if(epnum<10):
                        episode = "0" + episode
                    replacement_idx = pidx
                    replacement_string = f"S{season}E{episode}"

            if found:
                fparts = fparts[:replacement_idx]
                fparts.append(replacement_string)
                fparts.append(file.ext)

            # Build the input value
            finput.value = ".".join(fparts)