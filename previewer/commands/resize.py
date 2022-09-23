"""
command line interface
"""

from argparse import ONE_OR_MORE, ArgumentParser, BooleanOptionalAction, Namespace
from pathlib import Path

from wand.image import Image

from ..resolution import Resolution
from ..utils import auto_resize_img, check_image, color_str, parser_group, save_img


def configure(parser: ArgumentParser):
    parser.set_defaults(handler=run)

    ## Generated file
    with parser_group(parser, name="output file options") as group:
        group.add_argument(
            "-o",
            "--output",
            type=Path,
            metavar="FOLDER",
            help="output folder (default is same directory as the original image)",
        )
        group.add_argument(
            "-P",
            "--prefix",
            help="generated filename prefix",
        )
        group.add_argument(
            "-S",
            "--suffix",
            help="generated filename suffix",
        )

    ## Geometry
    with parser_group(parser, name="image geometry") as group:
        group.add_argument(
            "--size",
            type=Resolution,
            metavar="WIDTHxHEIGHT",
            required=True,
            help="thumbnail size",
        )
        group.add_argument(
            "--crop",
            action=BooleanOptionalAction,
            default=False,
            help="crop thumbnails",
        )
        group.add_argument(
            "--fill",
            action=BooleanOptionalAction,
            default=False,
            help="fill thumbnails",
        )

    parser.add_argument(
        "images",
        nargs=ONE_OR_MORE,
        type=Path,
        help="images to resize",
    )


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
