from os import getenv
from pathlib import Path
from shutil import copy2, copytree
from tempfile import TemporaryDirectory
from urllib.request import urlretrieve

from pytest import fixture

URL_IMAGE1 = "https://download.samplelib.com/jpeg/sample-clouds-400x300.jpg"
URL_IMAGE2 = "https://download.samplelib.com/jpeg/sample-city-park-400x300.jpg"
URL_IMAGE3 = "https://download.samplelib.com/jpeg/sample-birch-400x300.jpg"
URL_VIDEO = "https://download.samplelib.com/mp4/sample-10s.mp4"


def check_file(file: Path) -> Path:
    assert file.exists()
    assert file.stat().st_size > 0
    return file


def download(url: str, file: Path) -> Path:
    print(">>> download", url, "->", file)
    assert not file.exists()
    file.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(url, file)
    return file


def pytest_sessionfinish(session, exitstatus):
    session.MY_TMP.cleanup()


def pytest_sessionstart(session):
    session.MY_TMP = TemporaryDirectory()

    samples_dir = Path(getenv("SAMPLES_DIR", session.MY_TMP.name))

    if getenv("SKIP_DOWNLOAD", "false").lower() != "true":
        # the gallery contains 9 images
        gallery = samples_dir / "gallery"
        gallery.mkdir()
        jpg1 = download(URL_IMAGE1, gallery / "01.jpg")
        jpg2 = download(URL_IMAGE2, gallery / "02.jpg")
        jpg3 = download(URL_IMAGE3, gallery / "03.jpg")
        copy2(jpg1, gallery / "04.jpg")
        copy2(jpg2, gallery / "05.jpg")
        copy2(jpg3, gallery / "06.jpg")
        copy2(jpg1, gallery / "07.jpg")
        copy2(jpg2, gallery / "08.jpg")
        copy2(jpg3, gallery / "09.jpg")
        # and a subfolder with 3 images
        (gallery / "subfolder").mkdir()
        copy2(jpg1, gallery / "subfolder" / "01.jpg")
        copy2(jpg2, gallery / "subfolder" / "02.jpg")
        copy2(jpg3, gallery / "subfolder" / "03.jpg")
        # a 10 seconds sample video
        download(URL_VIDEO, samples_dir / "sample.mp4")

    session.SAMPLES_DIR = samples_dir


@fixture
def tmp_path_with_samples(request, tmp_path) -> Path:
    copytree(request.session.SAMPLES_DIR, tmp_path, dirs_exist_ok=True)
    return tmp_path


@fixture
def sample_mp4(tmp_path_with_samples: Path) -> Path:
    return check_file(tmp_path_with_samples / "sample.mp4")


@fixture
def sample_gallery(tmp_path_with_samples: Path) -> Path:
    return tmp_path_with_samples / "gallery"


@fixture
def sample_jpg(sample_gallery: Path) -> Path:
    return check_file(sample_gallery / "01.jpg")


@fixture
def sample2_jpg(sample_gallery: Path) -> Path:
    return check_file(sample_gallery / "02.jpg")
