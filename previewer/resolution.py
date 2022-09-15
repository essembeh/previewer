from pathlib import Path
from re import fullmatch
from typing import Tuple

from wand.image import Image

_PATTERN = r"(?P<width>[0-9]+)(x(?P<height>[0-9]+))?"


class Resolution:
    __slots__ = ("width", "height")

    @classmethod
    def from_image(cls, image: Path):
        with Image(filename=image) as img:
            return cls(img.width, img.height)

    @classmethod
    def from_img(cls, img: Image):
        return cls(img.width, img.height)

    def __init__(self, *args):
        """
        accept parameter
        200
        200, 300
        "200"
        "200x300"
        """
        if len(args) == 1:
            value = args[0]
            if isinstance(value, int):
                self.height = self.width = value
            elif isinstance(value, str):
                matcher = fullmatch(_PATTERN, value)
                assert matcher is not None
                self.width = int(matcher.group("width"))
                self.height = (
                    int(matcher.group("height"))
                    if matcher.group("height") is not None
                    else int(matcher.group("width"))
                )
        elif len(args) == 2:
            self.width, self.height = int(args[0]), int(args[1])

        assert (
            self.width is not None and self.height is not None
        ), f"Invalid resolution: {', '.join(args)}"
        assert self.width > 0 and self.height > 0

    @property
    def x(self):
        return self.width

    @property
    def y(self):
        return self.height

    @property
    def size(self) -> Tuple[int, int]:
        return (self.width, self.height)

    def __str__(self):
        return f"{self.width}x{self.height}"

    def __eq__(self, other):
        """
        resolutions are equal if both have same width and same height
        """
        return (
            isinstance(other, Resolution)
            and self.width == other.width
            and self.height == other.height
        )
