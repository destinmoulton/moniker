from pathlib import Path
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Label, Button, Input, RadioSet, RadioButton, Checkbox, Static

from context import Context, MediaType

class SettingsForm(Vertical):
    ctx: Context

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.ctx.on("settingsform:save", self.save_settings)

    def compose(self) -> ComposeResult:
        configpath = self.ctx.config.get_full_config_path()

        moviepath = self.ctx.config.get("paths", "movies")
        showpath = self.ctx.config.get("paths", "shows")

        with VerticalScroll(id="settingsform-top-container"):
            yield Label("Settings")
            yield Static(f"Config file: {configpath}")
            yield Label("Path to Movies")
            yield Input(id="settingsform-input-movies-path",
                        classes="settingsform-input",
                        value=moviepath)
            yield Label("Path to Shows")
            yield Input(id="settingsform-input-shows-path",
                        classes="settingsform-input",
                        value=showpath)

        yield SettingsFormButtonBar(id="destination-button-bar", ctx=self.ctx)


    def save_settings(self, event):
        input_moviepath = self.query_one("#settingsform-input-movies-path")
        input_showspath = self.query_one("#settingsform-input-shows-path")

        # validate the paths
        moviepath = input_moviepath.value
        showspath = input_showspath.value

        error = False
        if not Path.is_dir(moviepath):
            error = True
            self.ctx.logger.write_line(f"ERROR: Movie directory does not exist: {moviepath}")

        if not Path.is_dir(showspath):
            error = True
            self.ctx.logger.write_line(f"ERROR: Shows directory does not exist: {showspath}")

        if not error:
            self.ctx.config.set("paths", "movies", moviepath)
            self.ctx.config.set("paths", "shows", showspath)
            self.ctx.config.save()
            params = {"screen": "browser"}
            self.ctx.emit("screen:change", params)

class SettingsFormButtonBar(Horizontal):
    ctx: Context

    def __init__(self, id, ctx):
        super().__init__(id=id)
        self.ctx = ctx

    def compose(self) -> ComposeResult:
        yield Button(label="Save Settings", id="settingsform-button-save", variant="success")

    def on_button_pressed(self, event: Button.Pressed)->None:
        if event.button.id == "settingsform-button-save":
            self.ctx.emit("settingsform:save", {})

