from shutil import copy2

from previewer.utils import *


def test_list_images(sample_gallery):
    assert len(list(iter_images_in_folder(sample_gallery, recursive=False))) == 9
    assert len(list(iter_images_in_folder(sample_gallery, recursive=True))) == 12


def test_copy_and_resize_images(sample_gallery, tmp_path):
    target_folder = tmp_path / "out"
    images = list(iter_images_in_folder(sample_gallery, recursive=False))
    assert len(images) == 9
    resized = list(
        map(
            lambda x: copy2(*x),
            iter_copy_tree(sample_gallery, target_folder, recursive=False, mkdirs=True),
        )
    )
    assert len(resized) == 9
    assert len(list(iter_images_in_folder(target_folder, recursive=False))) == 9
    assert len(list(iter_images_in_folder(target_folder, recursive=True))) == 9


def test_copy_and_resize_images_recursive(sample_gallery, tmp_path):
    target_folder = tmp_path / "out"
    images = list(iter_images_in_folder(sample_gallery, recursive=True))
    assert len(images) == 12
    resized = list(
        map(
            lambda x: copy2(*x),
            iter_copy_tree(sample_gallery, target_folder, recursive=True, mkdirs=True),
        )
    )
    assert len(resized) == 12
    assert len(list(iter_images_in_folder(target_folder, recursive=False))) == 9
    assert len(list(iter_images_in_folder(target_folder, recursive=True))) == 12


def test_color_str(tmp_path):
    assert color_str(tmp_path) == str(tmp_path)


def test_image(sample_gallery):
    count = 0
    for jpg in sample_gallery.glob("*.jpg"):
        assert is_image(jpg)
        assert not is_video(jpg)
        count += 1
    assert count == 9


def test_video(sample_mp4):
    assert not is_image(sample_mp4)
    assert is_video(sample_mp4)
