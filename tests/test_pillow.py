from PIL import Image, ImageFilter, ImageOps

from previewer import filters
from previewer.montage import build_montage


def test_resize_image(image):
    with Image.open(image) as img:
        assert img.size == (800, 600)
        img2 = filters.Resize((100, 100)).apply(img)
        assert img2.size == (100, 75)


def test_crop_fill_image(image):
    with Image.open(image) as img:
        assert img.size == (800, 600)
        img2 = filters.CropFill((200, 100)).apply(img)
        assert img2.size == (200, 100)


def test_crop_fit_image(image):
    with Image.open(image) as img:
        assert img.size == (800, 600)
        img2 = filters.CropFit((200, 100)).apply(img)
        assert img2.size == (200, 100)


def test_blur_image(image):
    with Image.open(image) as img:
        assert img.size == (800, 600)
        img2 = img.filter(ImageFilter.GaussianBlur(radius=20))
        assert img2.size == (800, 600)


def test_shadow_image(image):
    with Image.open(image) as img:
        assert img.size == (800, 600)
        img2 = filters.Shadow(margin=0.1, size=0.05).apply(img)
        assert img2.size == (800 + 80 * 2 + 40, 600 + 80 * 2 + 40)


def test_montage(image):
    images = []
    with Image.open(image) as img:
        images.append(ImageOps.fit(img, (200, 100)))
        images.append(ImageOps.fit(img, (150, 200)))
        images.append(ImageOps.fit(img, (250, 120)))
        images.append(ImageOps.fit(img, (300, 200)))
        images.append(ImageOps.fit(img, (200, 150)))

    img2 = build_montage(images, 3)
    assert img2.size == (300 + 200 + 250 + 10 * 4, 200 + 200 + 10 * 3)


def test_polaroid(image):

    with Image.open(image) as img:
        assert img.size == (800, 600)
        img2 = filters.Polaroid().apply(img)
        assert img2.size == (860, 780)
