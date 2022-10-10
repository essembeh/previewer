"""
Wand related manipulation functions
"""
from wand.image import Image

from .resolution import Resolution
from .tools.resize import ImageResizer


def auto_resize_img(
    image: Image, resolution: Resolution, crop: bool, fill: bool
) -> Image:
    """
    Resize/crop the given image
    """
    return ImageResizer(resolution=resolution, fill=fill, crop=crop).transform(image)
