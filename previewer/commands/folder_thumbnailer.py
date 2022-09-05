"""
command line interface
"""

import traceback
from argparse import ArgumentParser
from os import getenv
from pathlib import Path

from .. import __version__
from ..resolution import Resolution
from ..utils import color_str, copy_and_resize_images, iter_images


def run():
    """
    entry point
    """
    parser = ArgumentParser(description="extract thumbnails from folder")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="list images recursively (only for images folders)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("."),
        help="output folder, default is current folder",
    )
    parser.add_argument(
        "-s",
        "--size",
        type=Resolution,
        default=Resolution(256, 256),
        help="thumbnails max size (default is 256x256)",
    )
    parser.add_argument(
        "--crop",
        action="store_true",
        help="crop thumbnails",
    )
    parser.add_argument("folder", nargs=1, type=Path, help="folder containing images")
    args = parser.parse_args()

    try:
        folder = args.folder[0]
        assert folder.is_dir(), f"Invalid folder: {folder}"

        images = list(iter_images(folder, recursive=args.recursive))
        assert len(images) > 0, f"Folder {folder} does not contain any image"

        print(
            f"📷 Generate {len(images)} thumbnails from {color_str(folder)} to {color_str(args.output)}"
        )
        for image, resized_image in copy_and_resize_images(
            folder, images, args.output, args.size, crop=args.crop
        ):
            print(f"  {color_str(image)} -> {color_str(resized_image)}")
    except KeyboardInterrupt:  # pylint: disable=broad-except
        print("❌ Process interrupted")
        exit(1)
    except BaseException as error:  # pylint: disable=broad-except
        print(f"💥 Cannot generate thumbnails: {color_str(error)}")
        if getenv("DEBUG") == "1":
            traceback.print_exc()
