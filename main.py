import argparse

from appconfig import AppConfig
from browser import Browser
from destination import Destination
from logger import Logger
from context import Context

from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, VerticalScroll, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Placeholder, DirectoryTree, Log, Checkbox, Button

from mover import Mover
from settingsform import SettingsForm


class Header(Placeholder):
    DEFAULT_CSS = """
    Header {
        height: 1;
        dock: top;
    }
    """


class MonikerScreen(Screen):
    ctx: Context

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.ctx.on("screen:change", self.__change_screen)
        self.settingsform = SettingsForm(self.ctx)
        self.browser = Browser(self.ctx)
        self.mover = Mover(self.ctx)
        self.destination = Destination(self.ctx)
        self.mover.settingsform = False
        self.mover.display = False
        self.destination.display = False

    def compose(self) -> ComposeResult:
        yield Header(id="Header", label="Moniker")
        with Horizontal(id="screen-container"):
            yield self.settingsform
            yield self.browser
            yield self.mover
            yield self.destination

        yield self.ctx.logger

        if not self.ctx.config.is_configured():
            self.__change_screen({"screen":"settingsform"})

    def __change_screen(self, event: dict):
        #container = self.query_one("#screen-container")
        if event["screen"] == "settingsform":
            self.settingsform.display = True
            self.browser.display = False
            self.mover.display = False
            self.destination.display = False
        elif event["screen"] == "mover":
            self.settingsform.display = False
            self.browser.display = False
            self.mover.display = True
            self.destination.display = False
        elif event["screen"] == "browser":
            self.settingsform.display = False
            self.browser.display = True
            self.mover.display = False
            self.destination.display = False
        elif event["screen"] == "destination":
            self.settingsform.display = False
            self.browser.display = False
            self.mover.display = False
            self.destination.display = True

        self.ctx.emit("screen:change:complete", event)



class LayoutApp(App):
    ctx: Context
    CSS_PATH = "styles.css"
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    def on_ready(self) -> None:
        self.push_screen(MonikerScreen(self.ctx))


if __name__ == "__main__":
    # Shared context object
    ctx = Context()
    ctx.logger = Logger()
    ctx.config = AppConfig()

    parser = argparse.ArgumentParser(prog="moniker", description="moniker moves and renames files")
    parser.add_argument("directory", default=".", help="starting directory")
    ctx.cliargs = parser.parse_args()

    app = LayoutApp(ctx)
    app.run()