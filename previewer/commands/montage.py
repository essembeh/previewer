"""
command line interface
"""
# pylint: disable=logging-fstring-interpolation

from argparse import ONE_OR_MORE, ArgumentParser, BooleanOptionalAction, Namespace
from datetime import timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from ..imagemagick import Montage
from ..resolution import Resolution
from ..utils import (
    auto_resize_image,
    color_str,
    is_video,
    iter_images_in_folder,
    parser_group,
)
from ..video import Position, get_video_duration, iter_video_frames


def configure(parser: ArgumentParser):
    parser.set_defaults(handler=run)

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
            help="start position (default: 5%)",
        )
        group.add_argument(
            "--end",
            type=Position,
            metavar="POSITION",
            default="-5%",
            help="end position (default: -5%)",
        )

    ## Montage options
    with parser_group(parser, name="montage options") as group:
        group.add_argument(
            "--polaroid",
            action=BooleanOptionalAction,
            help="use polaroid style",
        )
        group.add_argument(
            "--shadow",
            action=BooleanOptionalAction,
            help="add shadow to thumbnails",
        )
        group.add_argument(
            "--title",
            action=BooleanOptionalAction,
            default=True,
            help="add file/folder name as preview title",
        )
        group.add_argument(
            "--filenames",
            action=BooleanOptionalAction,
            help="add filenames under thumbnails",
        )
        group.add_argument(
            "--font",
            help="font used for labels, use 'convert -list font' to list available fonts",
        )
        group.add_argument(
            "-b",
            "--background",
            help="montage background color, list of colors: https://imagemagick.org/script/color.php",
        )
        group.add_argument(
            "-c",
            "--columns",
            type=int,
            default=6,
            help="preview columns count (default is 6)",
        )
        group.add_argument(
            "--offset",
            type=int,
            default=10,
            help="thumbnail offset (default is 10)",
        )

    ## Geometry
    with parser_group(parser, name="image geometry") as group:
        default_size = Resolution(256, 256)
        group.add_argument(
            "--size",
            type=Resolution,
            metavar="WIDTHxHEIGHT",
            default=default_size,
            help=f"thumbnail size (default: {default_size})",
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
            default=True,
            help="fill thumbnails",
        )

    parser.add_argument(
        "input_files",
        type=Path,
        nargs=ONE_OR_MORE,
        help="folders containing images or video files",
    )


def run(args: Namespace):
    montage = Montage(
        background=args.background,
        columns=args.columns,
        th_size=args.size,
        th_offset=args.offset,
        font=args.font,
    )
    if args.polaroid is not None:
        montage.polaroid = args.polaroid
    if args.shadow is not None:
        montage.shadow = args.shadow

    for folder_or_video in args.input_files:
        output_jpg = (
            (args.output or Path())
            / f"{args.prefix or ''}{folder_or_video.name if folder_or_video.is_dir() else folder_or_video.stem}{args.suffix or ''}.jpg"
        )
        if output_jpg.exists():
            print(
                f"💡 Preview {color_str(output_jpg)} already generated from {color_str(folder_or_video)}"
            )
            continue

        with TemporaryDirectory() as tmp:
            tmp_folder = Path(tmp)
            if folder_or_video.is_dir():
                run_folder(args, montage, folder_or_video, output_jpg, tmp_folder)
            elif is_video(folder_or_video):
                run_video(args, montage, folder_or_video, output_jpg, tmp_folder)
            else:
                print(f"🙈 {color_str(folder_or_video)} is not a folder nor a video")


def run_folder(
    args: Namespace, montage: Montage, folder: Path, output_jpg: Path, tmp_folder: Path
):
    count = len(list(iter_images_in_folder(folder, recursive=args.recursive)))
    assert count > 0, "Folder does not contain any image"
    print(
        f"📷 Generate montage from folder {color_str(folder)} containing {count} images"
    )
    montage.build(
        (
            auto_resize_image(
                image,
                tmp_folder / image.name,
                resolution=args.size,
                crop=args.crop,
                fill=args.fill,
            )
            for image in iter_images_in_folder(folder, recursive=args.recursive)
        ),
        output_jpg,
        filenames=args.filenames,
        title=folder.name if args.title else None,
    )
    print(f"🍺 Montage generated {color_str(output_jpg)}")


def run_video(
    args: Namespace, montage: Montage, video: Path, output_jpg: Path, tmp_folder: Path
):
    count = args.count or (args.columns * args.columns)
    print(f"🎬 Generate montage from video {color_str(video)} using {count} thumbnails")
    duration = get_video_duration(video)
    start = args.start.get_seconds(duration)
    end = args.end.get_seconds(duration)
    montage.build(
        (
            auto_resize_image(
                frame,
                tmp_folder / f"{timedelta(seconds=position)}.jpg",
                resolution=args.size,
                crop=args.crop,
                fill=args.fill,
            )
            for frame, position in iter_video_frames(video, count, start=start, end=end)
        ),
        output_jpg,
        filenames=args.filenames,
        title=video.name if args.title else None,
    )
    print(f"🍺 Montage generated {color_str(output_jpg)}")
