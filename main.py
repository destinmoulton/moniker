import argparse

from appconfig import AppConfig
from browser import Browser
from confirm import Confirm
from logger import Logger
from context import Context

from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, VerticalScroll, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Placeholder, DirectoryTree, Log, Checkbox, Button

from parser import Parser
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
        self.parser = Parser(self.ctx)
        self.confirm = Confirm(self.ctx)
        self.settingsform.display = False
        self.parser.display = False
        self.confirm.display = False



    def compose(self) -> ComposeResult:
        yield Header(id="Header", label="Moniker")
        with Horizontal(id="screen-container"):
            yield self.settingsform
            yield self.browser
            yield self.parser
            yield self.confirm

        yield self.ctx.logger


        if not self.ctx.config.is_configured():
            self.__change_screen({"screen":"settingsform"})

    def __change_screen(self, event: dict):
        #container = self.query_one("#screen-container")
        if event["screen"] == "settingsform":
            self.settingsform.display = True
            self.browser.display = False
            self.parser.display = False
            self.confirm.display = False
        elif event["screen"] == "browser":
            self.ctx.reset_all()
            self.ctx.emit("browser:refresh", {})
            self.settingsform.display = False
            self.browser.display = True
            self.parser.display = False
            self.confirm.display = False
        elif event["screen"] == "parser":
            self.settingsform.display = False
            self.browser.display = False
            self.parser.display = True
            self.confirm.display = False
        elif event["screen"] == "confirm":
            self.settingsform.display = False
            self.browser.display = False
            self.parser.display = False
            self.confirm.display = True

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