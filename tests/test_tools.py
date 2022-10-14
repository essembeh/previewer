from previewer.resolution import Resolution
from previewer.tools.resizer import ImageResizer
from previewer.tools.sequence import create_sequence
from previewer.utils import get_mime
from wand.image import Image


def test_resize_fit(sample_jpg):
    with Image(filename=sample_jpg) as img:
        assert img.size == (400, 300)
        img = ImageResizer(Resolution(120, 120), crop=False, fill=False).transform(img)
        assert img.size == (120, 90)


def test_resize_fill(sample_jpg):
    with Image(filename=sample_jpg) as img:
        assert img.size == (400, 300)
        img = ImageResizer(Resolution(120, 120), crop=False, fill=True).transform(img)
        assert img.size == (160, 120)


def test_crop_fit(sample_jpg):
    with Image(filename=sample_jpg) as img:
        assert img.size == (400, 300)
        img = ImageResizer(Resolution(120, 120), crop=True, fill=False).transform(img)
        assert img.size == (120, 120)


def test_crop_fill(sample_jpg):
    with Image(filename=sample_jpg) as img:
        assert img.size == (400, 300)
        img = ImageResizer(Resolution(120, 120), crop=True, fill=True).transform(img)
        assert img.size == (120, 120)


def test_create_sequence(sample_jpg, sample2_jpg, tmp_path):
    with Image(filename=sample_jpg) as img1, Image(filename=sample2_jpg) as img2:
        out = tmp_path / "01.gif"
        create_sequence([img1, img2], out)
        assert get_mime(out) == "image/gif"
