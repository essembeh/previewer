"""
command line interface
"""

from argparse import ONE_OR_MORE, ArgumentParser, Namespace
from pathlib import Path

from wand.image import Image

from ..utils import check_image, color_str, save_img
from .utils import add_geometry_group, get_image_resizer, parser_group


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
    add_geometry_group(parser, resolution_required=True)

    parser.add_argument(
        "images",
        nargs=ONE_OR_MORE,
        type=Path,
        help="images to resize",
    )


def run(args: Namespace):
    resizer = get_image_resizer(args)
    for source_image in args.images:
        output_folder = args.output or source_image.parent
        print(
            f"{'Crop' if args.crop else 'Resize'} {color_str(source_image)} to {'fill' if args.fill else 'fit'} {args.size}"
        )
        with Image(filename=check_image(source_image)) as img:
            img = resizer.transform(img)
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
