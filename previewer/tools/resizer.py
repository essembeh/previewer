"""
Wand related manipulation functions
"""
import shutil
import time
from dataclasses import dataclass
from pathlib import Path

from wand.image import GRAVITY_TYPES, Image

from ..logger import DEBUG
from ..resolution import Resolution
from ..utils import save_img
from .blur import DEFAULT_BLUR, BlurGenerator


@dataclass
class ImageResizer:
    """
    Utility class to blur an image
    """

    resolution: Resolution
    keep_aspect_ratio: bool = True
    fill: bool = True
    crop: bool = True
    crop_gravity: str = "center"
    crop_blur: BlurGenerator = DEFAULT_BLUR

    def __post_init__(self):
        assert (
            self.crop_gravity in GRAVITY_TYPES
        ), f"Invalid gravity {self.crop_gravity}, must be {GRAVITY_TYPES}"

    def transform_file(self, source: Path, dest: Path) -> Path:
        if self.resolution is None or Resolution.from_image(source) == self.resolution:
            # fallback copy, image
            return shutil.copy2(source, dest)
        else:
            with Image(filename=source) as img:
                save_img(self.transform(img), dest)
        return dest

    def transform(self, image: Image) -> Image:
        """
        Resize the given image
        """
        start = time.time()
        orig_size = Resolution.from_img(image)
        if self.resolution is None:
            # do nothing
            pass
        elif orig_size == self.resolution:
            # nothing to do
            pass
        elif self.crop:
            # crop
            if self.fill:
                # crop and fill
                image.transform(resize=f"{self.resolution}^")
                image.crop(
                    width=self.resolution.width,
                    height=self.resolution.height,
                    gravity=self.crop_gravity,
                )
            else:
                # crop and fit
                with image.clone() as thumbnail:
                    # resize thumbnail
                    thumbnail.transform(resize=f"{self.resolution}")
                    if thumbnail.size == self.resolution.size:
                        # no need to generate background
                        image.transform(resize=f"{self.resolution}")
                    else:
                        # blur the image as filling background
                        if self.keep_aspect_ratio:
                            image.transform(resize=f"{self.resolution}^")
                        else:
                            image.transform(resize=f"{self.resolution}!")
                        image.crop(
                            width=self.resolution.width,
                            height=self.resolution.height,
                            gravity=self.crop_gravity,
                        )
                        image = self.crop_blur.transform(image)
                        image.composite(
                            thumbnail,
                            left=int((self.resolution.width - thumbnail.width) / 2),
                            top=int((self.resolution.height - thumbnail.height) / 2),
                        )
        else:
            # resize
            if not self.keep_aspect_ratio:
                # force size
                image.transform(resize=f"{self.resolution}!")
            elif self.fill:
                # resize and fill
                image.transform(resize=f"{self.resolution}^")
            else:
                # resize and fit
                image.transform(resize=f"{self.resolution}")
        DEBUG(
            "%s and %s image from %s -> %s (%.1f seconds)",
            "Crop" if self.crop else "Resize",
            "force" if self.keep_aspect_ratio else ("fill" if self.fill else "fit"),
            orig_size,
            Resolution.from_img(image),
            time.time() - start,
        )
        return image
