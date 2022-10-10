from previewer.tools.montage import Montage
from previewer.utils import iter_images_in_folder


def test_montage(tmp_path, sample_gallery):
    output = tmp_path / "output.jpg"
    montage = Montage(font="DejaVu-Sans")
    command = montage.build(iter_images_in_folder(sample_gallery), output)
    assert output.exists()
    assert " -tile 6 " in command


def test_montage_filenames(tmp_path, sample_gallery):
    output = tmp_path / "output.jpg"
    montage = Montage(font="DejaVu-Sans")
    command = montage.build(
        iter_images_in_folder(sample_gallery), output, filenames=True
    )
    assert output.exists()
    assert " -label " in command


def test_montage_title(tmp_path, sample_gallery):
    output = tmp_path / "output.jpg"
    montage = Montage(font="DejaVu-Sans")
    command = montage.build(
        iter_images_in_folder(sample_gallery), output, title="Some title"
    )
    assert output.exists()
    assert " -title " in command


def test_montage_background(tmp_path, sample_gallery):
    output = tmp_path / "output.jpg"
    montage = Montage(font="DejaVu-Sans", background="pink")
    command = montage.build(iter_images_in_folder(sample_gallery), output)
    assert output.exists()
    assert " -background pink " in command


def test_montage_col(tmp_path, sample_gallery):
    output = tmp_path / "output.jpg"
    montage = Montage(font="DejaVu-Sans", columns=1)
    command = montage.build(iter_images_in_folder(sample_gallery), output)
    assert output.exists()
    assert " -tile 1 " in command


def test_montage_polaroid(tmp_path, sample_gallery):
    output = tmp_path / "output1.jpg"
    montage = Montage(font="DejaVu-Sans", polaroid=False)
    command = montage.build(iter_images_in_folder(sample_gallery), output)
    assert output.exists()
    assert " +polaroid " not in command

    output = tmp_path / "output2.jpg"
    montage = Montage(font="DejaVu-Sans", polaroid=True)
    command = montage.build(iter_images_in_folder(sample_gallery), output)
    assert output.exists()
    assert " +polaroid " in command


def test_montage_shadow(tmp_path, sample_gallery):
    output = tmp_path / "output1.jpg"
    montage = Montage(font="DejaVu-Sans", shadow=False)
    command = montage.build(iter_images_in_folder(sample_gallery), output)
    assert output.exists()
    assert " -shadow " not in command

    output = tmp_path / "output2.jpg"
    montage = Montage(font="DejaVu-Sans", shadow=True)
    command = montage.build(iter_images_in_folder(sample_gallery), output)
    assert output.exists()
    assert " -shadow " in command
