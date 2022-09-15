from previewer.imagemagick import Montage
from previewer.utils import iter_images_in_folder


def test_montage(tmp_path, gallery_dir):
    output = tmp_path / "output.jpg"
    montage = Montage()
    command = montage.build(iter_images_in_folder(gallery_dir), output)
    assert output.exists()
    assert " -tile 6 " in command


def test_montage_filenames(tmp_path, gallery_dir):
    output = tmp_path / "output.jpg"
    montage = Montage()
    command = montage.build(iter_images_in_folder(gallery_dir), output, filenames=True)
    assert output.exists()
    assert " -label " in command


def test_montage_title(tmp_path, gallery_dir):
    output = tmp_path / "output.jpg"
    montage = Montage()
    command = montage.build(
        iter_images_in_folder(gallery_dir), output, title="Some title"
    )
    assert output.exists()
    assert " -title " in command


def test_montage_background(tmp_path, gallery_dir):
    output = tmp_path / "output.jpg"
    montage = Montage(background="pink")
    command = montage.build(iter_images_in_folder(gallery_dir), output)
    assert output.exists()
    assert " -background pink " in command


def test_montage_col(tmp_path, gallery_dir):
    output = tmp_path / "output.jpg"
    montage = Montage(columns=8)
    command = montage.build(iter_images_in_folder(gallery_dir), output)
    assert output.exists()
    assert " -tile 8 " in command


def test_montage_polaroid(tmp_path, gallery_dir):
    output = tmp_path / "output1.jpg"
    montage = Montage(polaroid=False)
    command = montage.build(iter_images_in_folder(gallery_dir), output)
    assert output.exists()
    assert " +polaroid " not in command

    output = tmp_path / "output2.jpg"
    montage = Montage(polaroid=True)
    command = montage.build(iter_images_in_folder(gallery_dir), output)
    assert output.exists()
    assert " +polaroid " in command


def test_montage_shadow(tmp_path, gallery_dir):
    output = tmp_path / "output1.jpg"
    montage = Montage(shadow=False)
    command = montage.build(iter_images_in_folder(gallery_dir), output)
    assert output.exists()
    assert " -shadow " not in command

    output = tmp_path / "output2.jpg"
    montage = Montage(shadow=True)
    command = montage.build(iter_images_in_folder(gallery_dir), output)
    assert output.exists()
    assert " -shadow " in command


def test_montage_auto_orient(tmp_path, gallery_dir):
    output = tmp_path / "output1.jpg"
    montage = Montage(auto_orient=False)
    command = montage.build(iter_images_in_folder(gallery_dir), output)
    assert output.exists()
    assert " -auto-orient " not in command

    output = tmp_path / "output2.jpg"
    montage = Montage(auto_orient=True)
    command = montage.build(iter_images_in_folder(gallery_dir), output)
    assert output.exists()
    assert " -auto-orient " in command
