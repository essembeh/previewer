"""
Wand related manipulation functions
"""
from dataclasses import dataclass

from wand.image import Image


@dataclass
class BlurGenerator:
    """
    Utility class to blur an image
    """

    blur_sigma: float
    black: float
    white: float
    gamma: float

    def transform(self, image: Image) -> Image:
        """
        Apply blur with given options
        """
        if self.blur_sigma > 0:
            image.gaussian_blur(sigma=self.blur_sigma)
        image.level(black=self.black, white=self.white, gamma=self.gamma)
        return image

    def __str__(self):
        return f"{self.blur_sigma}:{self.black}:{self.white}:{self.gamma}"


DEFAULT_BLUR = BlurGenerator(30, 0, 1, 0.7)
