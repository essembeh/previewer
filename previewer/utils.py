import sys
from pathlib import Path
from subprocess import check_call
from typing import Any, Iterable, Iterator, Tuple

import magic
from colorama import Fore, Style

from .tools import TOOLS


def is_video(file: Path) -> bool:
    """
    check if given file is a video
    """
    return file.exists() and magic.from_file(str(file.resolve()), mime=True).startswith(
        "video/"
    )


def is_image(file: Path) -> bool:
    """
    check if given file is an image
    """
    return file.exists() and magic.from_file(str(file.resolve()), mime=True).startswith(
        "image/"
    )


def color_str(item: Any) -> str:
    """
    colorize item given its type
    """
    if not sys.stdout.isatty():
        return str(item)
    if isinstance(item, Path):
        if item.is_dir():
            return f"{Fore.BLUE}{Style.BRIGHT}{item}/{Style.RESET_ALL}"
        return f"{Style.BRIGHT}{Fore.BLUE}{item.parent}/{Fore.MAGENTA}{item.name}{Style.RESET_ALL}"
    if isinstance(item, BaseException):
        return f"{Fore.RED}{item}{Fore.RESET}"
    return str(item)


def resize_image(source: Path, target: Path, size: int) -> Path:
    """
    create a copy of the given image with the given size
    """
    assert not target.exists(), f"File already exists: {target}"
    target.parent.mkdir(parents=True, exist_ok=True)
    check_call([TOOLS.convert, "-resize", f"{size}x{size}^", str(source), str(target)])
    return target


def iter_images(folder: Path, recursive: bool = False) -> Iterator[Path]:
    """
    list all image from given folder
    """
    assert folder.is_dir()
    for item in sorted(folder.iterdir()):
        if item.is_dir():
            if recursive:
                yield from iter_images(item, recursive=True)
        elif is_image(item):
            yield item


def copy_and_resize_images(
    source_folder: Path, files: Iterable[Path], dest_folder: Path, size: int
) -> Iterator[Tuple[Path, Path]]:
    """
    copy all image files from a folder and resize them on the fly
    """
    for file in files:
        yield file, resize_image(file, dest_folder / file.relative_to(source_folder), size)
