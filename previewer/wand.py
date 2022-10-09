"""
Wand related manipulation functions
"""
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable, Optional

from wand.image import GRAVITY_TYPES, Image

from .logger import DEBUG
from .resolution import Resolution


class Operation(Enum):
    CROP_BLUR = "crop with blur"
    CROP_FILL = "crop and fill"
    RESIZE_LOOSE = "resize"
    RESIZE_FIT = "resize fit"
    RESIZE_FILL = "resize fill"


@dataclass
class BlurGenerator:
    """
    Utility class to blur an image
    """

    blur_sigma: float
    black: float
    white: float
    gamma: float

    def apply(self, image: Image) -> Image:
        """
        Apply blur with given options
        """
        if self.blur_sigma > 0:
            image.gaussian_blur(sigma=self.blur_sigma)
        image.level(black=self.black, white=self.white, gamma=self.gamma)
        return image

    def __str__(self):
        return f"blur:{self.blur_sigma}:{self.black}:{self.white}:{self.gamma}"


DEFAULT_BLUR = BlurGenerator(30, 0, 1, 0.7)


@dataclass
class ImageResizer:
    """
    Utility class to resize/crop images
    """

    size: Resolution
    keep_aspect_ratio: bool = True
    fill: bool = True
    crop: bool = True
    crop_gravity: str = "center"
    crop_blur: BlurGenerator = DEFAULT_BLUR

    def __post_init__(self):
        assert (
            self.crop_gravity in GRAVITY_TYPES
        ), f"Invalid gravity {self.crop_gravity}, must be {GRAVITY_TYPES}"

    def resize(self, image: Image) -> Image:
        """
        Resize the given image
        """
        start = time.time()
        orig_size = Resolution.from_img(image)
        if self.size is None:
            # do nothing
            pass
        elif orig_size == self.size:
            # nothing to do
            pass
        elif self.crop:
            # crop
            if self.fill:
                # crop and fill
                image.transform(resize=f"{self.size}^")
                image.crop(
                    width=self.size.width,
                    height=self.size.height,
                    gravity=self.crop_gravity,
                )
            else:
                # crop and fit
                with image.clone() as thumbnail:
                    # resize thumbnail
                    thumbnail.transform(resize=f"{self.size}")
                    if thumbnail.size == self.size.size:
                        # no need to generate background
                        image.transform(resize=f"{self.size}")
                    else:
                        # blur the image as filling background
                        if self.keep_aspect_ratio:
                            image.transform(resize=f"{self.size}^")
                        else:
                            image.transform(resize=f"{self.size}!")
                        image.crop(
                            width=self.size.width,
                            height=self.size.height,
                            gravity=self.crop_gravity,
                        )
                        self.crop_blur.apply(image)
                        image.composite(
                            thumbnail,
                            left=int((self.size.width - thumbnail.width) / 2),
                            top=int((self.size.height - thumbnail.height) / 2),
                        )
        else:
            # resize
            if not self.keep_aspect_ratio:
                # force size
                image.transform(resize=f"{self.size}!")
            elif self.fill:
                # resize and fill
                image.transform(resize=f"{self.size}^")
            else:
                # resize and fit
                image.transform(resize=f"{self.size}")
        DEBUG(
            "%s and %s image from %s -> %s (%.1f seconds)",
            "Crop" if self.crop else "Resize",
            "force" if self.keep_aspect_ratio else ("fill" if self.fill else "fit"),
            orig_size,
            Resolution.from_img(image),
            time.time() - start,
        )
        return image


def auto_resize_img(
    image: Image,
    resolution: Resolution,
    crop: bool,
    fill: bool,
) -> Image:
    """
    Resize/crop the given image
    """
    orig_size = Resolution.from_img(image)

    if resolution is not None and resolution.size != image.size:
        start = time.time()
        if crop and fill:
            crop_fill(image, resolution)
        elif crop and not fill:
            crop_fit(image, resolution)
        elif not crop and fill:
            resize_fill(image, resolution)
        elif not crop and not fill:
            resize_fit(image, resolution)
        DEBUG(
            "resize image from %s -> %s, crop=%s, fill=%s (%.1f seconds)",
            orig_size,
            Resolution.from_img(image),
            crop,
            fill,
            time.time() - start,
        )
    else:
        DEBUG(
            "skip resizing image to %s, crop=%s, fill=%s",
            Resolution.from_img(image),
            crop,
            fill,
        )
    return image


def resize_fit(image: Image, resolution: Resolution) -> Image:
    """
    Resize an image to fit the given dimensions
    """
    image.transform(
        resize=f"{resolution.width}x{resolution.height}",
    )
    return image


def resize_fill(image: Image, resolution: Resolution) -> Image:
    """
    Resize an image to fill the given dimensions
    """
    image.transform(
        resize=f"{resolution.width}x{resolution.height}^",
    )
    return image


def crop_fill(image: Image, resolution: Resolution) -> Image:
    """
    Crop an image to given dimensions
    """
    image.transform(
        resize=f"{resolution.width}x{resolution.height}^",
    )
    image.crop(width=resolution.width, height=resolution.height, gravity="center")
    return image


def crop_fit(
    image: Image,
    resolution: Resolution,
    bg_keep_ratio: bool = False,
    blur: BlurGenerator = DEFAULT_BLUR,
):
    """
    Crop an image to given dimensions, adding a blur to fill the background
    """
    with image.clone() as thumbnail:
        # resize thumbnail
        thumbnail.transform(resize=f"{resolution.width}x{resolution.height}")
        if thumbnail.size == resolution.size:
            # no need to generate background
            image.transform(resize=f"{resolution.width}x{resolution.height}")
        else:
            # blur the image as filling background
            image.transform(
                resize=f"{resolution.width}x{resolution.height}{'^' if bg_keep_ratio else '!'}"
            )
            image.crop(
                width=resolution.width, height=resolution.height, gravity="center"
            )
            blur.apply(image)

            image.composite(
                thumbnail,
                left=int((resolution.width - thumbnail.width) / 2),
                top=int((resolution.height - thumbnail.height) / 2),
            )

    return image


def montage(
    thumbnails: Iterable[Image],
    output: Path,
    columns: int,
    border: int = 10,
    shadow: bool = True,
):
    """
    Create a montage
    """
    with Image() as out:

        for thumbnail in thumbnails:
            out.image_add(thumbnail)

        out.montage(
            tile=f"{columns}x",
            mode="frame" if shadow else "unframe",
            frame="1" if shadow else "0",
            thumbnail=f"+{border}+{border}",
        )
        out.save(filename=output)


def create_gif(
    frames: Iterable[Image],
    output_file: Path,
    delay: int = 50,
    optimize: bool = True,
    aba_loop: Optional[str] = None,
):
    """
    Create a gif with the given images
    """
    with Image() as gif:
        queue = []
        for frame in frames:
            gif.sequence.append(frame)
            if aba_loop is not None:
                queue.append(frame.clone())
        if aba_loop is not None:
            # if A-B-A mode, add image in reverse order
            queue.reverse()
            if aba_loop == "aba" and len(queue) > 2:
                # skip first and last to prevent 2 identical consecutive frames
                queue.pop(0).destroy()
                queue.pop(-1).destroy()
            for frame in queue:
                gif.sequence.append(frame)
                # ba frames are reated
                frame.destroy()

        # TODO: try to use optimize_transparency/optimize_layers/coalesce for optimizations

        DEBUG("set gif delay to %d", delay)
        for frame in gif.sequence:
            frame.delay = delay
        if optimize:
            gif.type = "optimize"
        gif.save(filename=output_file)
