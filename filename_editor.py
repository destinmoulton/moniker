import re
from typing import Tuple
from textual import events
from textual import log

from context import Context, MediaType, MediaTypeRegex

from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.app import ComposeResult
from textual.widgets import Label, Button, Input, RadioSet, RadioButton, Checkbox

from file import File

FILE_PARTS_TO_IGNORE = [
    "1080p", "720p", "webrip", "amzn", "aac", "eng", "x264", "x265", "bluray", "xvid", "yify"
]

class FilenameEditor(Vertical):
    ctx: Context

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    def compose(self) -> ComposeResult:
        with Horizontal(id="parser-top-container"):
            yield EditorLeftColumn(id="parser-left-column", ctx=self.ctx)
            with Vertical(id="parser-right-column"):
                yield FilenameFields(id="parser-file-fields-container", ctx=self.ctx)

        yield EditorButtonBar(id="parser-button-bar", ctx=self.ctx)


class EditorButtonBar(Horizontal):
    ctx: Context

    def __init__(self, id, ctx):
        super().__init__(id=id)
        self.ctx = ctx

    def compose(self) -> ComposeResult:
        yield Button(label="Back", id="parser-button-back")
        yield Button(label="Next", id="parser-button-next", variant="success")

    def on_button_pressed(self, event: Button.Pressed)->None:
        if event.button.id == "parser-button-back":
            params = {"screen":"browser"}
            self.ctx.reset_guessed()
            self.ctx.emit("screen:change", params)
        elif event.button.id =="parser-button-next":
            params = {"screen":"confirm"}
            self.ctx.emit("screen:change", params)
            self.ctx.emit("fe:save", {})


class EditorLeftColumn(VerticalScroll):
    ctx: Context

    def __init__(self, id, ctx):
        super().__init__(id=id)
        self.ctx = ctx
        self.regex_box = RegexWidget(id="parser-regex-box", ctx=ctx)
        self.guessed_details_box = GuessedMediaDetailsWidget(id="parser-movieshow-details", ctx=self.ctx)

    def compose(self) -> ComposeResult:
        yield Label("Media Type")
        with RadioSet():
            yield RadioButton("Movie - Year", classes="parser-radio-mediatype", id="parser-radio-movie", value=(self.ctx.selected["mediatype"] is MediaType.MOVIE))
            yield RadioButton("Show - Season and Episode (S##E##)", classes="parser-radio-mediatype", id="parser-radio-show", value=(self.ctx.selected["mediatype"] is MediaType.SHOW))
        yield Label("Regex")
        with Vertical():
            yield self.regex_box
        yield self.guessed_details_box

    def _on_show(self, event: events.Show) -> None:
        self.__set_active_mediatype()

    def on_radio_set_changed(self, event):
        self.__handle_change_mediatype()
        self.guessed_details_box.toggle_section()

    def __handle_change_mediatype(self):
        radios = self.query(".parser-radio-mediatype")
        for radio in radios:
            if radio.value:
                if radio.id== "parser-radio-show":
                    sel = MediaType.SHOW
                elif radio.id== "parser-radio-movie":
                    sel = MediaType.MOVIE

                self.ctx.set_selected_mediatype(sel)
                self.regex_box.set_regex_input_value(MediaTypeRegex[sel])

    def __set_active_mediatype(self):
        radios = self.query(".parser-radio-mediatype")
        for radio in radios:
            # start by resetting radios
            radio.value = False
            if radio.id == "parser-radio-show" and self.ctx.selected['mediatype'] is MediaType.SHOW:
                radio.value = True
            elif radio.id=="parser-radio-movie" and self.ctx.selected['mediatype'] is MediaType.MOVIE:
                radio.value = True

        self.__handle_change_mediatype()


class RegexWidget(Vertical):
    ctx: Context

    def __init__(self, id, ctx):
        super().__init__(id=id)
        self.ctx = ctx
        self.regex_input = Input(id="parser-input-regex", classes="parser-input", value=MediaTypeRegex[self.ctx.selected['mediatype']])

    def compose(self)->ComposeResult:
        yield self.regex_input
        yield Button(label="Run Regex", id="regex-button-run", variant="success")

    def on_button_pressed(self, event: Button.Pressed)->None:
        if event.button.id == "regex-button-run":
            regex_pattern = self.__compile_regex()
            if regex_pattern != False:
                self.ctx.regex["string"] = self.regex_input.value
                self.ctx.regex["pattern"] = regex_pattern
                self.ctx.regex["is_valid"] = True

                # regex is valid so guess the media details
                self.__guess_media_details()

                self.ctx.emit("fe:regex:changed", {"value": self.regex_input.value})
            else:
                self.ctx.regex["is_valid"] = False

    def set_regex_input_value(self, newvalue):
        self.regex_input.value = newvalue

    def __compile_regex(self):
        try:
            return re.compile(self.ctx.regex["string"])
        except re.error as e:
            self.ctx.logger.write_line(f"ERROR: Invalid regex {e}")
        return False

    def __guess_media_details(self)->None:
        regex_pattern = self.ctx.regex['pattern']
        for fid, file in self.ctx.selected["files"].items():
            found = False
            title_end_idx = 0
            match = regex_pattern.search(file.path.name)

            if match:
                if self.ctx.selected['mediatype']==MediaType.SHOW:
                    found, title_end_idx = self.__match_season_episode(match, fid)
                elif self.ctx.selected['mediatype']==MediaType.MOVIE:
                    found, title_end_idx = self.__match_movie_year(match)

            if found:
                # clean up the title
                title = file.path.name[:title_end_idx]
                # remove whitespace from ends
                title = title.strip()
                # replace spaces with periods
                title = title.replace(" ", ".")

                self.ctx.set_guessed_title(title)

    def __match_season_episode(self, match:re.Match, fid: str)->tuple[bool,int]:
        if len(match.groups()) == 2:
            title_end_idx = match.start(1)-1
            seasnum = int(match.group(1))
            epnum = int(match.group(2))

            season = str(seasnum)
            if (seasnum < 10):
                season = f"0{season}"

            episode = str(epnum)
            if (epnum < 10):
                episode = f"0{episode}"

            self.ctx.set_guessed_episode(fid, f"E{episode}")
            self.ctx.set_guessed_season(f"S{season}")
            return True, title_end_idx
        return False, 0

    def __match_movie_year(self, match:re.Match)->tuple[bool,int]:
        if len(match.groups()) == 1:
            title_end_idx = match.start(1)-1
            year = match.group(1)
            self.ctx.set_guessed_year(year)
            return True, title_end_idx
        return False, 0


class GuessedMediaDetailsWidget(Vertical):
    ctx: Context
    def __init__(self, id, ctx):
        super().__init__(id=id)
        self.ctx = ctx
        self.movie_details = Vertical()
        self.show_details = Vertical()
        self.movie_details.display = False
        self.show_details.display = False
        self.input_title = Input(id="guessed-title",
                            classes="parser-details-widget",
                            value=self.ctx.guessed['title'])
        self.input_year = Input(id="guessed-year",
                            classes="parser-details-widget",
                            value=self.ctx.guessed['year'])
        self.input_season = Input(id="guessed-season",
                            classes="parser-details-widget",
                            value=self.ctx.guessed['season'])
        self.ctx.on("fe:regex:changed", self.__handle_regex_changed)

    def compose(self) -> ComposeResult:
        yield Label("Title",
                            classes="parser-details-widget")
        yield self.input_title
        with self.movie_details:
            yield Label("Movie Year",
                               classes = "parser-details-widget")
            yield self.input_year
        with self.show_details:
            yield Label("Show Season",
                                 classes="parser-details-widget")
            yield self.input_season
        yield Button(label="Apply", id="guessed-try-it-button", variant="success")

    def on_button_pressed(self, event: Button.Pressed)->None:
        if event.button.id == "guessed-try-it-button":
            self.ctx.emit("fe:fields:update", {})

    def on_input_changed(self, event)->None:
        if event.input.id == "guessed-title":
            self.ctx.set_guessed_title(event.input.value)
        elif event.input.id == "guessed-year":
            self.ctx.set_guessed_year(event.input.value)
        elif event.input.id == "guessed-season":
            self.ctx.set_guessed_season(event.input.value)

    def toggle_section(self):
        if self.ctx.selected['mediatype'] is MediaType.MOVIE:
            self.movie_details.display = True
            self.show_details.display = False
        elif self.ctx.selected['mediatype'] is MediaType.SHOW:
            self.movie_details.display = False
            self.show_details.display = True

    def __handle_regex_changed(self, event):
        possible_title = self.ctx.guessed['title']
        self.input_title.value = possible_title

        if self.ctx.selected['mediatype'] is MediaType.MOVIE:
            self.input_year.value = self.ctx.guessed['year']
        elif self.ctx.selected['mediatype'] is MediaType.SHOW:
            self.input_season.value = self.ctx.guessed['season']



class FilenameFields(VerticalScroll):
    ctx: Context
    def __init__(self, id, ctx):
        super().__init__(id=id)
        self.ctx = ctx
        self.ctx.on("fe:fields:update", self.__handle_update_fields)

    def on_show(self) -> None:
        self.__build_fields()

    def on_input_changed(self, event)->None:
        self.ctx.set_final_filename(event.input.data['fid'], event.input.value)

    def __build_fields(self)->None:
        # Clear the verticals from the container
        self.query(Vertical).remove()

        self.ctx.debug_selected_files()
        for fid, file in self.ctx.selected["files"].items():
            fieldgroup = Vertical(classes="parser-file-fieldgroup")
            self.mount(fieldgroup)

            fieldgroup.mount(Label(content=file.path.name, classes="parser-file-original"))

            filename_initial_value = file.path.name
            filename_input = Input(id=f"parser-file-{fid}", classes="parser-input", value=filename_initial_value)
            filename_input.data = {"fid":fid}

            fieldgroup.mount(filename_input)
            self.ctx.set_final_filename(fid, filename_initial_value)

        self.refresh(layout=True)
        self.__update_file_fields()

    def __save_fielddata(self, event)->None:
        self.ctx.final['filenames'] = {}

        for fid, file in self.ctx.selected["files"].items():
            input = self.query_one(f"#parser-file-{fid}")
            self.ctx.final['filenames'][fid] = input.value

    def __regex_changed(self, event)->None:
        self.__update_file_fields()

    def __handle_update_fields(self, event):
        self.__update_file_fields()

    def __update_file_fields(self)->None:
        filename_prefix = self.ctx.guessed['title']
        for fid, file in self.ctx.selected["files"].items():
            finput = self.query_one(f"#parser-file-{fid}")

            ext = file.ext
            if fid in self.ctx.final_filenames:
                filename = self.ctx.final_filenames[fid]
            else:
                filename = f"{file.path.name}"

            if self.ctx.selected['mediatype']==MediaType.SHOW:
                season = self.ctx.guessed['season']
                if fid in self.ctx.guessed['episodes']:
                    episode = self.ctx.guessed['episodes'][fid]
                    filename = f"{filename_prefix}.{season}{episode}.{ext}"

            elif self.ctx.selected['mediatype']==MediaType.MOVIE:
                year = self.ctx.guessed['year']
                filename = f"{filename_prefix}.{year}.{ext}"

            self.ctx.set_final_filename(fid, filename)
            finput.value = filename