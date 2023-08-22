from dataclasses import dataclass, field
from random import randrange
from typing import List

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


class DummyFilter:
    """
    Apply a filter on an image
    """

    def apply(self, image: Image.Image) -> Image.Image:
        return image


@dataclass
class MultiFilters(DummyFilter):
    filters: List[DummyFilter] = field(default_factory=list)

    def add(self, filter_: DummyFilter):
        self.filters.append(filter_)

    def apply(self, image: Image.Image) -> Image.Image:
        out = image
        for filter_ in self.filters:
            out = filter_.apply(out)
        return out


@dataclass
class AutoOrient(DummyFilter):
    def apply(self, image: Image.Image) -> Image.Image:
        return ImageOps.exif_transpose(image)


@dataclass
class Resize(DummyFilter):
    size: tuple[int, int]

    def apply(self, image: Image.Image) -> Image.Image:
        out = image.copy()
        out.thumbnail(self.size)
        return out


@dataclass
class CropFill(DummyFilter):
    size: tuple[int, int]

    def apply(self, image: Image.Image) -> Image.Image:
        return ImageOps.fit(image, self.size)


@dataclass
class CropFit(DummyFilter):
    size: tuple[int, int]
    blur_radius: int = 10
    blur_brightness: float = 0.8
    keep_ratio: bool = True

    def apply(self, image: Image.Image) -> Image.Image:
        # background image
        out = (
            ImageOps.fit(image, self.size)
            if self.keep_ratio
            else image.resize(self.size)
        )
        # blur it
        out = out.filter(ImageFilter.GaussianBlur(radius=self.blur_radius))
        # adjust brightness
        out = ImageEnhance.Brightness(out).enhance(self.blur_brightness)
        # actual thumbnail
        resized_image = image.copy()
        resized_image.thumbnail(self.size)
        # paste the thumbnail on the background
        out.paste(
            resized_image,
            (
                int((out.size[0] - resized_image.size[0]) / 2),
                int((out.size[1] - resized_image.size[1]) / 2),
            ),
        )
        return out


@dataclass
class Shadow(DummyFilter):
    """
    Inspired from https://en.wikibooks.org/wiki/Python_Imaging_Library/Drop_Shadows
    """

    size: float = 0.03
    margin: float = 0.05
    background_color: str = "#ffffff"
    shadow_color: str = "#020202"
    shadow_blur_radius: float = 0.02

    def apply(self, image: Image.Image) -> Image.Image:
        size = int(max(image.size) * self.size)
        return Shadow.apply_shadow(
            image,
            offset=(size, size),
            margin=int(max(image.size) * self.margin),
            shadow_blur_radius=int(max(image.size) * self.shadow_blur_radius),
            background_color=self.background_color,
            shadow_color=self.shadow_color,
        )

    @staticmethod
    def apply_shadow(
        image: Image.Image,
        offset: tuple[int, int],
        margin: int,
        shadow_blur_radius: int,
        background_color: str,
        shadow_color: str,
    ) -> Image.Image:
        # Calculate the size of the shadow's image
        width = image.size[0] + abs(offset[0]) + 2 * margin
        height = image.size[1] + abs(offset[1]) + 2 * margin

        # Create the shadow's image. Match the parent image's mode.
        out = Image.new(image.mode, (width, height), background_color)

        # Place the shadow, with the required offset
        # if <0, push the rest of the image right
        shadow_left = margin + max(offset[0], 0)
        # if <0, push the rest of the image down
        shadow_top = margin + max(offset[1], 0)
        # Paste in the constant colour
        out.paste(
            shadow_color,
            (
                shadow_left,
                shadow_top,
                shadow_left + image.size[0],
                shadow_top + image.size[1],
            ),
        )

        # Apply the GaussianBlur filter
        out = out.filter(ImageFilter.GaussianBlur(radius=shadow_blur_radius))

        # Paste the original image on top of the shadow
        out.paste(image, (margin - min(offset[0], 0), margin - min(offset[1], 0)))

        return out


@dataclass
class Polaroid(DummyFilter):
    border: float = 0.05
    background_color: str = "#ffffff"
    frame_color: str = "#f8f6f1"

    def apply(self, image: Image.Image) -> Image.Image:
        border = int(min(image.size) * self.border)
        out = Image.new(
            image.mode,
            (image.size[0] + border * 2, image.size[1] + border * 6),
            self.frame_color,
        )
        out.paste(image, (border, border))
        return out


@dataclass
class Rotation(DummyFilter):
    angle: int = 0
    expand: bool = True
    random: bool = False
    background_color: str = "#ffffff"

    def apply(self, image: Image.Image) -> Image.Image:
        angle = randrange(self.angle * -1, self.angle) if self.random else self.angle
        return image.rotate(angle, expand=self.expand, fillcolor=self.background_color)
