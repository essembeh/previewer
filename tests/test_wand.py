from previewer.utils import get_mime
from previewer.wand import *
from wand.image import Image


def test_resize_fit(sample1_jpg):
    with Image(filename=sample1_jpg) as img:
        assert img.size == (400, 300)
        img = resize_fit(img, Resolution(120, 120))
        assert img.size == (120, 90)


def test_resize_fill(sample1_jpg):
    with Image(filename=sample1_jpg) as img:
        assert img.size == (400, 300)
        img = resize_fill(img, Resolution(120, 120))
        assert img.size == (160, 120)


def test_crop_fit(sample1_jpg):
    with Image(filename=sample1_jpg) as img:
        assert img.size == (400, 300)
        img = crop_fit(img, Resolution(120, 120))
        assert img.size == (120, 120)


def test_crop_fill(sample1_jpg):
    with Image(filename=sample1_jpg) as img:
        assert img.size == (400, 300)
        img = crop_fill(img, Resolution(120, 120))
        assert img.size == (120, 120)


def test_create_gif(sample1_jpg, sample2_jpg, tmp_path):
    with Image(filename=sample1_jpg) as img1, Image(filename=sample2_jpg) as img2:
        out = tmp_path / "01.gif"
        create_gif([img1, img2], out)
        assert get_mime(out) == "image/gif"
