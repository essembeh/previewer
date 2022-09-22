from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from wand.image import Image

from .logger import DEBUG
from .resolution import Resolution


@dataclass
class BlurGenerator:
    blur_sigma: float
    black: float
    white: float
    gamma: float

    def apply(self, image: Image) -> Image:
        if self.blur_sigma > 0:
            image.gaussian_blur(sigma=self.blur_sigma)
        image.level(black=self.black, white=self.white, gamma=self.gamma)

    def __str__(self):
        return f"blur:{self.blur_sigma}:{self.black}:{self.white}:{self.gamma}"


DEFAULT_BLUR = BlurGenerator(30, 0, 1, 0.7)


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
        if crop and fill:
            crop_fill(image, resolution)
        elif crop and not fill:
            crop_fit(image, resolution)
        elif not crop and fill:
            resize_fill(image, resolution)
        elif not crop and not fill:
            resize_fit(image, resolution)
    DEBUG(
        "resize image from %s -> %s, crop=%s, fill=%s",
        orig_size,
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
    blur: BlurGenerator = DEFAULT_BLUR,
    bg_keep_ratio: bool = False,
):
    """
    Crop an image to given dimensions, adding a blur to fill the background
    """
    with image.clone() as thumbnail:
        # resize thumbnail
        thumbnail.transform(
            resize=f"{resolution.width}x{resolution.height}",
        )

        # blur the image as filling background
        image.transform(
            resize=f"{resolution.width}x{resolution.height}{'^' if bg_keep_ratio else '!'}",
        )
        image.crop(width=resolution.width, height=resolution.height, gravity="center")
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
    output_gif: Path,
    delay: int = 50,
    optimize: bool = True,
):
    """
    Create a gif with the given images
    """
    with Image() as gif:
        for frame in frames:
            gif.sequence.append(frame)
        DEBUG("set gif delay to %d", delay)
        for frame in gif.sequence:
            frame.delay = delay
        if optimize:
            gif.type = "optimize"
        gif.save(filename=output_gif)
