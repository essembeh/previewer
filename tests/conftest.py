from os import getenv
from pathlib import Path
from shutil import copy2

from pytest import fixture

SAMPLES_DIR = Path(__file__).parent / "samples"


def check_file(file: Path) -> Path:
    assert file.exists()
    assert file.stat().st_size > 0
    return file


@fixture
def image(tmp_path) -> Path:
    assert SAMPLES_DIR.is_dir()
    return check_file(copy2(SAMPLES_DIR / "800x600.jpg", tmp_path / "sample.jpg"))


@fixture
def clip(tmp_path) -> Path:
    assert SAMPLES_DIR.is_dir()
    return check_file(copy2(SAMPLES_DIR / "4sec.mp4", tmp_path / "sample.mp4"))
