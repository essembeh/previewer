import random
import shutil
import sys
from argparse import _ActionsContainer
from collections.abc import Iterable
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Iterator, Tuple

import magic
from colorama import Fore, Style

from wand.image import Image

from .resolution import Resolution
from .wand import auto_resize_img


def get_mime(file: Path) -> str:
    """
    Return the mime of a file
    """
    if not file.exists():
        raise FileNotFoundError(f"Cannot find file: {file}")
    return magic.from_file(str(file.resolve()), mime=True)


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
    return file.exists() and get_mime(file).startswith("image/")


def check_image(file: Path) -> Path:
    assert is_image(file), f"{file} is not a valid image"
    return file


def check_empty_folder(folder: Path):
    if folder.exists():
        assert folder.is_dir(), f"Invalid folder {folder}"
        assert next(folder.iterdir(), None) is None, f"Folder {folder} is not empty"
    else:
        folder.mkdir(parents=True)
    return folder


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


def iter_images_in_folder(
    folder: Path, recursive: bool = False, shuffle: bool = False
) -> Iterator[Path]:
    """
    list all image from given folder
    """
    assert folder.is_dir()
    items = list(folder.iterdir())
    if shuffle:
        random.shuffle(items)
    else:
        items = sorted(items)
    for item in items:
        if item.is_dir():
            if recursive:
                yield from iter_images_in_folder(item, recursive=True)
        elif is_image(item):
            yield item


def auto_resize_image(
    source: Path,
    destination: Path,
    resolution: Resolution,
    crop: bool,
    fill: bool,
) -> Path:
    """
    resize the given image
    """
    if resolution is not None:
        with Image(filename=source) as img:
            if resolution.size != img.size:
                return save_img(
                    auto_resize_img(img, resolution, crop=crop, fill=fill), destination
                )
    # fallback copy, image
    return shutil.copy2(source, destination)


def iter_img(images: Iterable[Path], auto_orient: bool = True) -> Iterator[Image]:
    for image in images:
        with Image(filename=image) as img:
            if auto_orient:
                img.auto_orient()
            yield img


def save_img(
    image: Image, dest: Path, overwrite: bool = False, mkdirs: bool = True
) -> Path:
    """
    Save an image with checks for overwrite and parent folder creation
    """
    if dest.exists():
        if not overwrite:
            raise FileExistsError(f"{dest} already exists")
    if mkdirs:
        dest.parent.mkdir(parents=True, exist_ok=True)
    image.save(filename=dest)
    return dest


def iter_copy_tree(
    source_folder: Path,
    destination_folder: Path,
    recursive: bool = False,
    mkdirs: bool = False,
) -> Iterator[Tuple[Path, Path]]:
    """
    iterator to copy folder recursively
    """
    for source_file in iter_images_in_folder(source_folder, recursive=recursive):
        destination_file = destination_folder / source_file.relative_to(source_folder)
        if mkdirs:
            destination_file.parent.mkdir(parents=True, exist_ok=True)
        yield source_file, destination_file


@contextmanager
def parser_group(
    parser: _ActionsContainer, name: str = "options group", exclusive: bool = False
) -> Generator[_ActionsContainer, None, None]:
    if exclusive:
        yield parser.add_mutually_exclusive_group()
    else:
        yield parser.add_argument_group(name)
