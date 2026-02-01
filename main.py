import argparse
import styles
from browser import Browser
from logger import Logger
from context import Context

from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, VerticalScroll, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Placeholder, DirectoryTree, Log, Checkbox, Button


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

    def compose(self) -> ComposeResult:
        yield Header(id="Header")
        with HorizontalScroll():
            yield Browser(self.ctx)

        yield self.ctx.logger


class LayoutApp(App):
    ctx: Context
    CSS = styles.CSS
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