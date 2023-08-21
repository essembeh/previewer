"""
command line interface
"""
import re
from argparse import (
    ONE_OR_MORE,
    ArgumentParser,
    BooleanOptionalAction,
    _ActionsContainer,
)
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from PIL import Image, ImageFont

from . import __version__
from .collectors import collect_folder_images, insert_timestamp, iter_video_frames
from .filters import CropFill, CropFit, DummyFilter, Resize, Shadow
from .font import list_fira_variants, load_fira_font
from .mime import is_video
from .montage import build_montage
from .resolution import resolution_parse
from .utils import color_str, save_img
from .video import Position, get_video_duration

DEFAULT_THUMBNAIL_SIZE = "640x480"


@contextmanager
def parser_group(
    parser: _ActionsContainer, name: str = "options group", exclusive: bool = False
) -> Generator[_ActionsContainer, None, None]:
    if exclusive:
        yield parser.add_mutually_exclusive_group()
    else:
        yield parser.add_argument_group(name)


def fix_hex_color(value: str) -> str:
    matcher = re.fullmatch(r"[0-9a-f]{6}", value, flags=re.IGNORECASE)
    return value if matcher is None else f"#{value}"


def run():
    """
    entry point
    """
    parser = ArgumentParser(description="preview generator")

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    ## Generated file
    with parser_group(parser, name="output file options") as group:
        group.add_argument(
            "-o",
            "--output",
            type=Path,
            metavar="FOLDER",
            help="output folder (default is current folder)",
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

    ## Folder only
    with parser_group(parser, name="only for folders") as group:
        group.add_argument(
            "-r",
            "--recursive",
            action="store_true",
            help="list images recursively",
        )

    ## Video only
    with parser_group(parser, name="only for videos") as group:
        group.add_argument(
            "-n",
            "--count",
            type=int,
            help="number of frames to extract (default: columns * columns)",
        )
        group.add_argument(
            "--start",
            type=Position,
            metavar="POSITION",
            default="5%",
            help="start position (default: 5%%)",
        )
        group.add_argument(
            "--end",
            type=Position,
            metavar="POSITION",
            default="-5%",
            help="end position (default: -5%%)",
        )
        group.add_argument(
            "--ts",
            action=BooleanOptionalAction,
            default=True,
            help="add timestamp to extracted frames",
        )

    ## Montage options
    with parser_group(parser, name="montage options") as group:
        group.add_argument(
            "--shadow",
            action=BooleanOptionalAction,
            help="add shadow to thumbnails",
        )
        group.add_argument(
            "-b",
            "--background",
            default="#ffffff",
            type=fix_hex_color,
            help="background color, use #123456 notation"
            + " or see https://github.com/python-pillow/Pillow/blob/main/src/PIL/ImageColor.py#L161",
        )
        group.add_argument(
            "-c",
            "--columns",
            type=int,
            default=6,
            help="preview columns count (default is 6)",
        )
        group.add_argument(
            "--margin",
            type=int,
            default=10,
            help="thumbnail margin (default is 10)",
        )

    ## Geometry
    with parser_group(parser, name="thumbnails options") as group:
        group.add_argument(
            "-s",
            "--size",
            type=resolution_parse,
            metavar="WIDTHxHEIGHT",
            default=DEFAULT_THUMBNAIL_SIZE,
            help=f"thumbnail size (default is {DEFAULT_THUMBNAIL_SIZE})",
        )
        group.add_argument(
            "--crop",
            action=BooleanOptionalAction,
            default=False,
            help="crop thumbnails",
        )
        with parser_group(group, exclusive=True) as xgroup:
            xgroup.add_argument(
                "--fill",
                action="store_const",
                dest="fill",
                const=True,
                default=True,
                help="fill thumbnails for crop mode",
            )
            xgroup.add_argument(
                "--fit",
                action="store_const",
                dest="fill",
                const=False,
                help="fit thumbnails for crop mode",
            )

    ## Text options
    with parser_group(parser, name="text options") as group:
        group.add_argument(
            "--title",
            action=BooleanOptionalAction,
            default=False,
            help="add file/folder name as image title",
        )
        group.add_argument(
            "--font-variant",
            type=str,
            choices=list_fira_variants(),
            help="font variant for text",
        )
        group.add_argument(
            "--font-size",
            type=int,
            help="font size for text",
        )
        group.add_argument(
            "--font-color",
            default="black",
            type=fix_hex_color,
            help="text color (default is black)",
        )

    ## input files
    parser.add_argument(
        "sources",
        type=Path,
        nargs=ONE_OR_MORE,
        help="folders containing images or video files",
    )
    args = parser.parse_args()

    pre_filter, post_filter = DummyFilter(), DummyFilter()
    if not args.crop:
        pre_filter = Resize(args.size)
    elif args.fill:
        pre_filter = CropFill(args.size)
    else:
        pre_filter = CropFit(args.size)

    if args.shadow:
        post_filter = Shadow(background_color=args.background)

    text_font = (
        load_fira_font(
            args.font_size if args.font_size is not None else int(args.size[1] / 10),
            variant=args.font_variant,
        )
        or ImageFont.load_default()
    )

    for source in args.sources:
        # target file
        output_jpg = (
            (args.output or Path())
            / f"{args.prefix or ''}{source.name if source.is_dir() else source.stem}{args.suffix or ''}.jpg"
        )
        if output_jpg.exists():
            print(
                f"💡 Preview {color_str(output_jpg)} already generated from {color_str(source)}"
            )
            continue

        # extract images
        images = []
        if source.is_dir():
            for image in collect_folder_images(source, recursive=args.recursive):
                # open file
                with Image.open(image) as img:
                    # apply resize
                    img = pre_filter.apply(img)
                    # apply other filter
                    img = post_filter.apply(img)

                    images.append(img)
            print(
                f"📷 Generate montage from folder {color_str(source)} containing {len(images)} images"
            )
        elif is_video(source):
            duration = get_video_duration(source)
            count = args.count or (args.columns * args.columns)
            print(
                f"🎬 Generate montage from video {color_str(source)} using {count} thumbnails"
            )
            for frame, ts in iter_video_frames(
                source,
                count=count,
                start=args.start.get_seconds(duration),
                end=args.end.get_seconds(duration),
            ):
                # open file
                with Image.open(frame) as img:
                    # apply resize
                    img = pre_filter.apply(img)
                    # insert timestamp
                    if args.ts:
                        img = insert_timestamp(img, ts, shadow=True)
                    # apply other filter
                    img = post_filter.apply(img)

                images.append(img)

        # build montage
        if len(images) == 0:
            print(f"🙈 Cannot find any image from {color_str(source)}")
        else:
            result = build_montage(
                images,
                columns=args.columns,
                margin=args.margin,
                background_color=args.background,
                text=source.name if args.title else None,
                text_font=text_font,
                text_color=args.font_color,
            )
            save_img(result, output_jpg)
            print(f"🍺 Montage generated {color_str(output_jpg)}")
