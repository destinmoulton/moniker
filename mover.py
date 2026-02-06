import re
from typing import Tuple
from textual import events

from context import Context, MediaType

from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.app import ComposeResult
from textual.widgets import Label, Button, Input, RadioSet, RadioButton, Checkbox

from file import File

FILE_PARTS_TO_IGNORE = [
    "1080p", "720p", "webrip", "amzn", "aac", "eng", "x264", "x265", "bluray", "xvid", "yify"
]

class Mover(Vertical):
    ctx: Context

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    def compose(self) -> ComposeResult:
        with Horizontal(id="mover-top-container"):
            yield MoverLeftColumn(id="mover-left-column", ctx=self.ctx)
            with Vertical(id="mover-right-column"):
                yield MoverFileFields(id="mover-file-fields-container", ctx=self.ctx)

        yield MoverButtonBar(id="mover-button-bar", ctx=self.ctx)


class MoverButtonBar(Horizontal):
    ctx: Context

    def __init__(self, id, ctx):
        super().__init__(id=id)
        self.ctx = ctx

    def compose(self) -> ComposeResult:
        yield Button(label="Back", id="mover-button-back")
        yield Button(label="Next", id="mover-button-next", variant="success")

    def on_button_pressed(self, event: Button.Pressed)->None:
        if event.button.id == "mover-button-back":
            params = {"screen":"browser"}
            self.ctx.emit("screen:change", params)
        elif event.button.id =="mover-button-next":
            params = {"screen":"destination"}
            self.ctx.emit("screen:change", params)


class MoverLeftColumn(VerticalScroll):
    ctx: Context
    default_regex: str =  {
        MediaType.SHOW:'[Ss](\d+)[Ee](\d+)',
        MediaType.MOVIE:'(19[0-9]{2}|2[0-9]{3})'
    }

    def __init__(self, id, ctx):
        super().__init__(id=id)
        self.ctx = ctx
        self.regex_input = Input(id="mover-input-regex", classes="mover-input", value=self.default_regex[self.ctx.selected['mediatype']])

    def compose(self) -> ComposeResult:
        yield Label("Identifier Regex")
        with RadioSet():
            yield RadioButton("Movie - Year", classes="mover-radio-mediatype", id="mover-radio-movie", value=(self.ctx.selected["mediatype"] is MediaType.MOVIE))
            yield RadioButton("Show - Season and Episode (S##E##)", classes="mover-radio-mediatype", id="mover-radio-show", value=(self.ctx.selected["mediatype"] is MediaType.SHOW))
        with Vertical():
            yield self.regex_input

    def _on_show(self, event: events.Show) -> None:
        self.__set_active_mediatype()

    def on_input_changed(self, event):
        if event.input.id == "mover-input-regex":
            self.ctx.regex = event.value
            self.ctx.emit("mover:regex:changed", {"value": event.value})

    def on_radio_set_changed(self, event):
        self.__handle_change_mediatype()

    def __handle_change_mediatype(self):
        radios = self.query(".mover-radio-mediatype")
        for radio in radios:
            if radio.value:
                if radio.id== "mover-radio-show":
                    sel = MediaType.SHOW
                    self.ctx.set_selected_mediatype(sel)
                    self.regex_input.value = self.default_regex[sel]
                elif radio.id== "mover-radio-movie":
                    sel = MediaType.MOVIE
                    self.ctx.set_selected_mediatype(sel)
                    self.regex_input.value = self.default_regex[sel]

    def __set_active_mediatype(self):
        radios = self.query(".mover-radio-mediatype")
        for radio in radios:
            # start by resetting radios
            radio.value = False
            if radio.id == "mover-radio-show" and self.ctx.selected['mediatype'] is MediaType.SHOW:
                radio.value = True
            elif radio.id=="mover-radio-movie" and self.ctx.selected['mediatype'] is MediaType.MOVIE:
                radio.value = True

        self.__handle_change_mediatype()


class FilePartSelector(Vertical):
    ctx: Context
    def __init__(self, id, ctx):
        super().__init__(id=id)
        self.ctx = ctx
        self.container = VerticalScroll(id="mover-fileparts-container")

    def compose(self)->ComposeResult:
        yield Label("Select Filename Parts")
        yield self.container

    def on_show(self) -> None:
        self.__update_file_part_checkboxes()

    def __update_file_part_checkboxes(self)->None:
        # build a set out of the possible file parts
        possibles = []
        for fid, file in self.ctx.selected["files"].items():
            for part in file.parts:
                tmppart = part.lower()
                if tmppart not in FILE_PARTS_TO_IGNORE:
                    if part not in possibles:
                        possibles.append(part)
        self.ctx.logger.write_line(f"Found possible parts {possibles}")
        # remove the current set of checkboxes
        checks = self.container.query(Checkbox)
        for check in checks:
            check.remove()

        for pidx, possible in enumerate(possibles):
            chk = Checkbox(label=possible)
            chk.data = possible
            self.container.mount(chk)


class MoverFileFields(VerticalScroll):
    ctx: Context
    def __init__(self, id, ctx):
        super().__init__(id=id)
        self.ctx = ctx
        self.ctx.on("mover:regex:changed", self.__regex_changed)

    def on_show(self) -> None:
        self.__build_fields()

    def __build_fields(self)->None:
        # Clear the verticals from the container
        self.query(Vertical).remove()

        self.ctx.debug_selected_files()
        for fid, file in self.ctx.selected["files"].items():
            fieldgroup = Vertical(classes="mover-file-fieldgroup")
            self.mount(fieldgroup)

            fieldgroup.mount(Label(file.path.name))
            fieldgroup.mount(Input(id=f"mover-file-{fid}", classes="mover-input", value=file.path.name))

        self.refresh(layout=True)
        self.update_file_fields()

    def __regex_changed(self, event)->None:
        self.update_file_fields()

    def update_file_fields(self)->None:
        regex = None

        try:
            regex = re.compile(self.ctx.regex)
        except re.error as e:
            self.ctx.logger.write_line(f"ERROR: Invalid regex {e}");

        for fid, file in self.ctx.selected["files"].items():
            finput = self.query_one(f"#mover-file-{fid}")
            fparts = file.parts.copy()

            replacement_string = ""
            replacement_idx = 0
            found = False
            for pidx, part in enumerate(fparts):
                if regex:
                    match = regex.search(part)

                    if match:
                        replacement_idx = pidx
                        if self.ctx.selected['mediatype']==MediaType.SHOW:
                            found, replacement_string = self.__match_season_episode(match)
                        elif self.ctx.selected['mediatype']==MediaType.MOVIE:
                            found, replacement_string = self.__match_movie_year(match)

            if found:
                fparts = fparts[:replacement_idx]

                # store the possible filename parts
                self.ctx.set_possible_nameparts(fparts.copy())

                fparts.append(replacement_string)
                fparts.append(file.ext)

            # Build the input value
            finput.value = ".".join(fparts)


    def __match_season_episode(self, match:re.Match)->Tuple[bool, str]:
        if len(match.groups()) == 2:
            seasnum = int(match.group(1))
            epnum = int(match.group(2))
            season = str(seasnum)
            if (seasnum < 10):
                season = "0" + season
            episode = str(epnum)
            if (epnum < 10):
                episode = "0" + episode
            self.ctx.set_possible_season(season)
            return True, f"S{season}E{episode}"
        return False, ""


    def __match_movie_year(self, match:re.Match)->Tuple[bool, str]:
        if len(match.groups()) == 1:
            year = match.group(1)
            self.ctx.set_possible_year(year)
            return True, f"{year}"
        return False, ""
