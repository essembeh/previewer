from shutil import copy2

from previewer.utils import *


def test_list_images(gallery_dir):
    assert len(list(iter_images_in_folder(gallery_dir, recursive=False))) == 2
    assert len(list(iter_images_in_folder(gallery_dir, recursive=True))) == 3


def test_copy_and_resize_images(gallery_dir, tmp_path):
    images = list(iter_images_in_folder(gallery_dir, recursive=False))
    assert len(images) == 2
    resized = list(
        map(
            lambda x: copy2(*x),
            iter_copy_tree(gallery_dir, tmp_path, recursive=False, mkdirs=True),
        )
    )
    assert len(resized) == 2
    assert len(list(iter_images_in_folder(tmp_path, recursive=False))) == 2
    assert len(list(iter_images_in_folder(tmp_path, recursive=True))) == 2


def test_copy_and_resize_images_recursive(gallery_dir, tmp_path):
    images = list(iter_images_in_folder(gallery_dir, recursive=True))
    assert len(images) == 3
    resized = list(
        map(
            lambda x: copy2(*x),
            iter_copy_tree(gallery_dir, tmp_path, recursive=True, mkdirs=True),
        )
    )
    assert len(resized) == 3
    assert len(list(iter_images_in_folder(tmp_path, recursive=False))) == 2
    assert len(list(iter_images_in_folder(tmp_path, recursive=True))) == 3


def test_color_str(tmp_path):
    assert color_str(tmp_path) == str(tmp_path)


def test_image(gallery_dir):
    count = 0
    for jpg in gallery_dir.glob("*.jpg"):
        assert is_image(jpg)
        assert not is_video(jpg)
        count += 1
    assert count == 2


def test_video(sample_mp4):
    assert not is_image(sample_mp4)
    assert is_video(sample_mp4)
