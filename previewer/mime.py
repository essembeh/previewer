from pathlib import Path

import puremagic


def get_mime(file: Path) -> str:
    """
    Return the mime of a file
    """
    if not file.exists():
        raise FileNotFoundError(f"Cannot find file: {file}")
    return puremagic.from_file(file.resolve(), mime=True)


def is_video(file: Path) -> bool:
    """
    check if given file is a video
    """
    return file.exists() and get_mime(file).startswith("video/")


def check_video(file: Path) -> Path:
    assert is_video(file), f"{file} is not a valid video file"
    return file


def is_image(file: Path) -> bool:
    """
    check if given file is an image
    """
    return file.is_file() and get_mime(file).startswith("image/")


def check_image(file: Path) -> Path:
    assert is_image(file), f"{file} is not a valid image"
    return file
