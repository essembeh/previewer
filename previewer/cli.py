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

from lazy_object_proxy import Proxy
from PIL import Image, ImageFont

from . import __version__
from .collectors import collect_folder_images, insert_timestamp, iter_video_frames
from .disposition import (
    best_disposition_from_columns,
    best_disposition_from_total,
    best_disposition_from_video,
)
from .filters import (
    AutoOrient,
    CropFill,
    CropFit,
    DummyFilter,
    MultiFilters,
    Polaroid,
    Resize,
    Rotation,
    Shadow,
)
from .font import list_fira_variants, load_fira_font
from .mime import is_video
from .montage import build_montage
from .resolution import resolution_parse
from .utils import color_str, save_img
from .video import Position, get_video_duration

DEFAULT_THUMBNAIL_SIZE = "400x400"


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


def parse_resize(size: str) -> DummyFilter:
    return Resize(resolution_parse(size))


def parse_crop(size: str) -> DummyFilter:
    return CropFill(resolution_parse(size))


def parse_cropfit(size: str) -> DummyFilter:
    return CropFit(resolution_parse(size))


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

    ## Effects options
    with parser_group(parser, name="effects", exclusive=True) as group:
        group.add_argument(
            "--polaroid",
            action=BooleanOptionalAction,
            help="add polaroid to thumbnails",
        )
        group.add_argument(
            "--shadow",
            action=BooleanOptionalAction,
            help="add shadow to thumbnails",
        )

    ## Montage options
    with parser_group(parser, name="montage options") as group:
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
            help="force the number of columns",
        )
        group.add_argument(
            "--margin",
            type=int,
            default=10,
            help="thumbnail margin (default is 10)",
        )
        group.add_argument(
            "--ratio",
            type=float,
            default=16 / 9,
            help="ratio used when columns number is automatically computed",
        )

    ## Geometry
    with parser_group(parser, name="resize options", exclusive=True) as group:
        group.add_argument(
            "-s",
            "--resize",
            type=lambda t: Resize(resolution_parse(t)),
            default=DEFAULT_THUMBNAIL_SIZE,
            dest="resize",
            metavar="WIDTHxHEIGHT",
            help=f"resize thumbnails (default is {DEFAULT_THUMBNAIL_SIZE})",
        )
        group.add_argument(
            "--crop",
            type=lambda t: CropFill(resolution_parse(t)),
            dest="resize",
            metavar="WIDTHxHEIGHT",
            help="crop thumbnails",
        )
        group.add_argument(
            "--crop-fit",
            type=lambda t: CropFit(resolution_parse(t)),
            dest="resize",
            metavar="WIDTHxHEIGHT",
            help="crop thumbnails and add blur background to fit the given size",
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
    orient_filter = AutoOrient()
    resize_filter = args.resize

    post_filters = MultiFilters()
    if args.shadow:
        post_filters.add(Shadow(background_color=args.background))
    elif args.polaroid:
        post_filters.add(Polaroid(background_color=args.background))
        post_filters.add(Shadow(background_color=args.background))
        post_filters.add(Rotation(15, random=True, background_color=args.background))

    text_font = (
        load_fira_font(
            args.font_size
            if args.font_size is not None
            else int(resize_filter.size[1] / 10),
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
        columns_count = args.columns
        if source.is_dir():
            ##########################################
            ## Extract from folder
            ##
            width_total, height_total = 0, 0
            for image in collect_folder_images(source, recursive=args.recursive):
                # open file
                with Image.open(image) as img:
                    # auto orient
                    img = orient_filter.apply(img)
                    # apply resize
                    img = resize_filter.apply(img)
                    width_total += img.width
                    height_total += img.height
                    # apply other filter
                    img = post_filters.apply(img)

                    images.append(img)
            # if no column number given, use best disposition
            if columns_count is None:
                disposition = best_disposition_from_total(
                    len(images),
                    resolution=(
                        int(width_total / len(images)),
                        int(height_total / len(images)),
                    ),
                    target_ratio=args.ratio,
                )
                columns_count = disposition.columns
            print(
                f"📷 Generate montage from folder {color_str(source)} containing {len(images)} images"
            )
        elif is_video(source):
            ##########################################
            ## Extract from video
            ##
            def get_first_frame_resolution():
                for frame, _ in iter_video_frames(source, 1):
                    with Image.open(frame) as img:
                        return args.resize.apply(img).size

            video_resolution = Proxy(get_first_frame_resolution)
            duration = get_video_duration(source)
            frame_count = args.count
            if columns_count is None and frame_count is None:
                disposition = best_disposition_from_video(
                    duration, resolution=video_resolution, target_ratio=args.ratio
                )
                columns_count = disposition.columns
                frame_count = disposition.images
            elif columns_count is None:
                # compute best disposition like what is done for folders
                disposition = best_disposition_from_total(
                    frame_count, resolution=video_resolution, target_ratio=args.ratio
                )
                columns_count = disposition.columns
            elif frame_count is None:
                # compute best disposition
                disposition = best_disposition_from_columns(
                    columns_count, resolution=video_resolution, target_ratio=args.ratio
                )
                frame_count = disposition.images
            print(
                f"🎬 Generate montage from video {color_str(source)} using {frame_count} thumbnails"
            )
            # extract frames
            for frame, ts in iter_video_frames(
                source,
                count=frame_count,
                start=args.start.get_seconds(duration),
                end=args.end.get_seconds(duration),
            ):
                # open file
                with Image.open(frame) as img:
                    # apply resize
                    img = resize_filter.apply(img)
                    # insert timestamp
                    if args.ts:
                        img = insert_timestamp(img, ts, shadow=True)
                    # apply other filter
                    img = post_filters.apply(img)

                images.append(img)

        ##########################################
        ## build montage
        ##
        if len(images) == 0:
            print(f"🙈 Cannot find any image from {color_str(source)}")
        else:
            result = build_montage(
                images,
                columns=columns_count,
                margin=args.margin,
                background_color=args.background,
                text=source.name if args.title else None,
                text_font=text_font,
                text_color=args.font_color,
            )
            save_img(result, output_jpg)
            print(f"🍺 Montage generated {color_str(output_jpg)}")
