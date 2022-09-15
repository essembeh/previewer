from os import getenv
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import urlretrieve

from pytest import fixture


def download(url: str, file: Path) -> Path:
    print(">>> download", url, "->", file)
    file.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(url, file)
    return file


def pytest_sessionstart(session):
    session.MY_TMP = TemporaryDirectory()

    samples_dir = getenv("SAMPLES_DIR")
    if samples_dir is not None:
        samples_dir = Path(samples_dir)
        session.SAMPLE_MP4 = samples_dir / "sample.mp4"
        session.SAMPLE_GALLERY = samples_dir / "gallery"
    else:
        session.SAMPLE_MP4 = download(
            "https://download.samplelib.com/mp4/sample-5s.mp4",
            Path(session.MY_TMP.name) / "sample.mp4",
        )
        session.SAMPLE_GALLERY = Path(session.MY_TMP.name) / "gallery"
        download(
            "https://download.samplelib.com/jpeg/sample-clouds-400x300.jpg",
            session.SAMPLE_GALLERY / "01.jpg",
        )
        download(
            "https://download.samplelib.com/jpeg/sample-clouds-400x300.jpg",
            session.SAMPLE_GALLERY / "02.jpg",
        )
        download(
            "https://download.samplelib.com/jpeg/sample-clouds-400x300.jpg",
            session.SAMPLE_GALLERY / "subfolder" / "01.jpg",
        )


def pytest_sessionfinish(session, exitstatus):
    session.MY_TMP.cleanup()


@fixture
def sample_mp4(request) -> Path:
    return request.session.SAMPLE_MP4


@fixture
def sample1_jpg(request) -> Path:
    return request.session.SAMPLE_GALLERY / "01.jpg"


@fixture
def sample2_jpg(request) -> Path:
    return request.session.SAMPLE_GALLERY / "02.jpg"


@fixture
def gallery_dir(request) -> Path:
    return request.session.SAMPLE_GALLERY
