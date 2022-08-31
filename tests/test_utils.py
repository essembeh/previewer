from previewer import utils


def test_list_images(gallery_dir):
    assert len(list(utils.iter_images(gallery_dir, recursive=False))) == 2
    assert len(list(utils.iter_images(gallery_dir, recursive=True))) == 3


def test_copy_and_resize_images(gallery_dir, tmp_path):
    images = list(utils.iter_images(gallery_dir, recursive=False))
    assert len(images) == 2
    resized = list(utils.copy_and_resize_images(gallery_dir, images, tmp_path, 100))
    assert len(resized) == 2
    assert len(list(utils.iter_images(tmp_path, recursive=False))) == 2
    assert len(list(utils.iter_images(tmp_path, recursive=True))) == 2


def test_copy_and_resize_images_recursive(gallery_dir, tmp_path):
    images = list(utils.iter_images(gallery_dir, recursive=True))
    assert len(images) == 3
    resized = list(utils.copy_and_resize_images(gallery_dir, images, tmp_path, 100))
    assert len(resized) == 3
    assert len(list(utils.iter_images(tmp_path, recursive=False))) == 2
    assert len(list(utils.iter_images(tmp_path, recursive=True))) == 3


def test_color_str(tmp_path):
    assert utils.color_str(tmp_path) == str(tmp_path)


def test_image(gallery_dir):
    count = 0
    for jpg in gallery_dir.glob("*.jpg"):
        assert utils.is_image(jpg)
        assert not utils.is_video(jpg)
        count += 1
    assert count == 2


def test_video(sample_mp4):
    assert not utils.is_image(sample_mp4)
    assert utils.is_video(sample_mp4)
