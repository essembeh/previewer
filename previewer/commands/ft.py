"""
command line interface
"""

from argparse import ONE_OR_MORE, ArgumentParser, BooleanOptionalAction, Namespace
from pathlib import Path

from ..resolution import Resolution
from ..utils import (
    auto_resize_image,
    check_empty_folder,
    color_str,
    iter_copy_tree,
    iter_images_in_folder,
)


def configure(parser: ArgumentParser):
    parser.set_defaults(handler=run)

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="output folder (default is a new folder in current directory)",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="list images recursively (only for images folders)",
    )
    parser.add_argument(
        "--size",
        type=Resolution,
        required=True,
        help="thumbnail size",
    )
    parser.add_argument(
        "--crop",
        action=BooleanOptionalAction,
        default=False,
        help="crop thumbnails (default is False)",
    )
    parser.add_argument(
        "--fill",
        action=BooleanOptionalAction,
        default=False,
        help="fill thumbnails (defailt is False)",
    )
    parser.add_argument(
        "folders", nargs=ONE_OR_MORE, type=Path, help="folders containging images"
    )


def run(args: Namespace):

    for input_folder in args.folders:
        output_folder = (
            check_empty_folder(Path(input_folder.name))
            if args.output is None
            else check_empty_folder(args.output)
        )

        print(f"Generate thumbnails from {color_str(input_folder)}")

        count = 0

        for source, destination in iter_copy_tree(
            input_folder, output_folder, recursive=args.recursive
        ):
            auto_resize_image(
                source, destination, args.size, crop=args.crop, fill=args.fill
            )
            print(f"  {color_str(destination)} ({Resolution.from_image(destination)})")
            count += 1

        print(f"🍺 {count} thumbnails generated in {color_str(output_folder)}")
