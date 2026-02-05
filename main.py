import argparse
from browser import Browser
from logger import Logger
from context import Context

from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, VerticalScroll, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Placeholder, DirectoryTree, Log, Checkbox, Button

from renamer import Renamer


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

        self.browser = Browser(self.ctx)
        self.renamer = Renamer(self.ctx)
        self.renamer.display = False

    def compose(self) -> ComposeResult:
        yield Header(id="Header", label="Moniker")
        with Horizontal(id="screen-container"):
            yield self.browser
            yield self.renamer

        yield self.ctx.logger

    def __change_screen(self, event: dict):
        #container = self.query_one("#screen-container")
        if event["screen"] == "renamer":
            self.browser.display = False
            self.renamer.display = True
        elif event["screen"] == "browser":
            self.browser.display = True
            self.renamer.display = False

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

    parser = argparse.ArgumentParser(prog="moniker", description="moniker moves and renames files")
    parser.add_argument("directory", default=".", help="starting directory")
    ctx.cliargs = parser.parse_args()

    app = LayoutApp(ctx)
    app.run()