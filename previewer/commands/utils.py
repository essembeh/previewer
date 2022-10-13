from argparse import ArgumentParser, BooleanOptionalAction, Namespace, _ActionsContainer
from contextlib import contextmanager
from typing import Generator, Optional

from wand.image import GRAVITY_TYPES

from ..resolution import Resolution
from ..tools.blur import DEFAULT_BLUR, BlurGenerator
from ..tools.resizer import ImageResizer


def get_image_resizer(args: Namespace) -> ImageResizer:
    """
    Build an image resizer given user parameters
    """
    return ImageResizer(
        resolution=args.size,
        keep_aspect_ratio=args.keep_ratio,
        fill=args.fill,
        crop=args.crop,
        crop_gravity=args.gravity,
        crop_blur=DEFAULT_BLUR
        if args.blur is None
        else BlurGenerator(
            blur_sigma=args.blur[0],
            black=args.blur[1],
            white=args.blur[2],
            gamma=args.blur[3],
        ),
    )


@contextmanager
def parser_group(
    parser: _ActionsContainer, name: str = "options group", exclusive: bool = False
) -> Generator[_ActionsContainer, None, None]:
    if exclusive:
        yield parser.add_mutually_exclusive_group()
    else:
        yield parser.add_argument_group(name)


def add_geometry_group(
    parser: ArgumentParser,
    resolution_required: bool = True,
    resolution_default: Optional[Resolution] = None,
    crop_default: bool = False,
    fill_default: bool = True,
):
    """
    add needed command line options to manipulate images
    """
    with parser_group(parser, name="image geometry") as group:
        group.add_argument(
            "-s",
            "--size",
            type=Resolution,
            metavar="WIDTHxHEIGHT",
            required=resolution_required,
            help="thumbnail size"
            + (f" (defailt: {resolution_default})" if resolution_default else ""),
        )
        group.add_argument(
            "--crop",
            action=BooleanOptionalAction,
            default=crop_default,
            help="crop thumbnails",
        )
        with parser_group(group, exclusive=True) as xgroup:
            xgroup.add_argument(
                "--fill",
                action="store_const",
                dest="fill",
                const=True,
                default=fill_default,
                help="fill thumbnails" + (" (default)" if fill_default else ""),
            )
            xgroup.add_argument(
                "--fit",
                action="store_const",
                dest="fill",
                const=False,
                help="fit thumbnails" + (" (default)" if not fill_default else ""),
            )

        group.add_argument(
            "--blur",
            type=lambda text: [float(x) for x in text.split(":")],
            help="blur option, format 'sigma:black:white:gamma' (float:float:float:float), "
            + f"default is {DEFAULT_BLUR}",
        )
        group.add_argument(
            "--keep-ratio",
            action=BooleanOptionalAction,
            default=True,
            help="keep original aspect when resizing",
        )
        group.add_argument(
            "--gravity",
            choices=GRAVITY_TYPES,
            default="center",
            help="for crop operation, use given gravity (default: 'center')",
        )
