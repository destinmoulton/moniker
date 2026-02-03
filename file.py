from pathlib import Path
from hashlib import md5
class File:
    path: Path = None
    ext: str = ""
    parts: list = []
    id: str = ""

    def __init__(self, path: Path):
        self.path = path

        # create a friendlier named local version of the extension
        self.ext = path.suffix.lstrip(".")

        self.__split_parts()
        self.__generate_id()

    def __split_parts(self):
        """ Split the file name into parts for renaming """
        if " " in self.path.name:
            self.parts = self.path.name.split(" ")
        elif "." in self.path.name:
            self.parts = self.path.name.split(".")

    def __generate_id(self):
        """ Generate md5 unique identifier for file """
        self.id = str(md5(str(self.path.name).encode("utf-8")).hexdigest())

