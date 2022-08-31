import sys
from pathlib import Path
from subprocess import check_call
from typing import Any, Generator, Iterable

import magic
from colorama import Fore, Style

from .tools import TOOLS


def is_video(file: Path) -> bool:
    """
    check if given file is a video
    """
    return magic.from_file(file, mime=True).startswith("video/")


def is_image(file: Path) -> bool:
    """
    check if given file is a video
    """
    return magic.from_file(file, mime=True).startswith("image/")


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


def iter_images(folder: Path, recursive: bool = False) -> Generator[Path, None, None]:
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
    source: Path, files: Iterable[Path], target: Path, size: int
) -> Generator[Path, None, None]:
    """
    copy all image files from a folder and resize them on the fly
    """
    for source_file in files:
        target_file = target / source_file.relative_to(source)
        target_file.parent.mkdir(parents=True, exist_ok=True)
        command = [TOOLS.convert, "-resize", f"{size}x{size}", source_file, target_file]
        assert not target_file.exists(), f"File already exists: {target_file}"
        check_call(list(map(str, command)))
        yield target_file
