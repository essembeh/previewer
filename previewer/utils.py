import sys
from pathlib import Path
from typing import Any

from colorama import Fore, Style
from PIL import Image


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


def save_img(
    image: Image.Image, dest: Path, overwrite: bool = False, mkdirs: bool = True
) -> Path:
    """
    Save an image with checks for overwrite and parent folder creation
    """
    if dest.exists():
        if not overwrite:
            raise FileExistsError(f"{dest} already exists")
    if mkdirs:
        dest.parent.mkdir(parents=True, exist_ok=True)
    image.save(dest)
    return dest
