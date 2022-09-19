"""
command line interface
"""

from argparse import ONE_OR_MORE, ArgumentParser, BooleanOptionalAction, Namespace
from pathlib import Path

from wand.image import Image

from ..resolution import Resolution
from ..utils import auto_resize_img, check_image, color_str, save_img


def configure(parser: ArgumentParser):
    parser.set_defaults(handler=run)

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="output folder (default is same directory as the original image)",
    )
    parser.add_argument(
        "-P",
        "--prefix",
        type=str,
        help="generated filename prefix",
    )
    parser.add_argument(
        "-S",
        "--suffix",
        type=str,
        help="generated filename prefix",
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
    parser.add_argument("images", nargs=ONE_OR_MORE, type=Path, help="images to resize")


def run(args: Namespace):
    for source_image in args.images:
        output_folder = args.output or source_image.parent
        print(
            f"{'Crop' if args.crop else 'Resize'} {color_str(source_image)} to {'fill' if args.fill else 'fit'} {args.size}"
        )
        with Image(filename=check_image(source_image)) as img:
            img = auto_resize_img(img, args.size, crop=args.crop, fill=args.fill)
            suffix = (
                args.suffix
                if args.suffix is not None
                else f" ({'crop' if args.crop else 'resize'}:{img.width}x{img.height})"
            )
            destination_image = (
                output_folder
                / f"{args.prefix or ''}{source_image.stem}{suffix}{source_image.suffix}"
            )

            if destination_image.exists():
                print(f"💡 Image {color_str(destination_image)} already exists")
            else:
                save_img(img, destination_image)
                print(
                    f"🍺 Generated {color_str(destination_image)} [{img.width}x{img.height}]"
                )
