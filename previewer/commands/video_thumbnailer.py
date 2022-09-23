from argparse import ONE_OR_MORE, ArgumentParser, BooleanOptionalAction, Namespace
from datetime import timedelta
from pathlib import Path

from ..resolution import Resolution
from ..utils import (
    auto_resize_image,
    check_empty_folder,
    check_video,
    color_str,
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
            help="generated filename prefix (default is video filename)",
        )
        group.add_argument(
            "-S",
            "--suffix",
            help="generated filename prefix (default frame time)",
        )

    ## Geometry
    with parser_group(parser, name="image geometry") as group:
        group.add_argument(
            "--size",
            type=Resolution,
            metavar="WIDTHxHEIGHT",
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

    with parser_group(parser, exclusive=True) as xgroup:
        xgroup.add_argument(
            "--fps",
            type=int,
            metavar="INT",
            help="frames per second",
        )
        xgroup.add_argument(
            "-n",
            "--count",
            type=int,
            default=20,
            help="thumbnails count (default is 20)",
        )

    parser.add_argument(
        "--start",
        type=Position,
        metavar="POSITION",
        default="5%",
        help="start position (default: 5%)",
    )
    parser.add_argument(
        "--end",
        type=Position,
        metavar="POSITION",
        default="-5%",
        help="end position (default: -5%)",
    )

    parser.add_argument(
        "videos",
        nargs=ONE_OR_MORE,
        type=Path,
        help="video files",
    )


def run(args: Namespace):
    for video in args.videos:
        video = check_video(video)
        folder = (
            check_empty_folder(args.output)
            if args.output is not None
            else check_empty_folder(Path(video.stem))
        )
        duration = get_video_duration(video)
        start = args.start.get_seconds(duration)
        end = args.end.get_seconds(duration)
        count = args.count if args.fps is None else int((end - start) * args.fps)
        print(f"Extract {count} thumbnails from {color_str(video)}")

        index = 0
        for frame, seconds in iter_video_frames(video, count, start=start, end=end):
            position = str(timedelta(seconds=int(seconds)))
            filename = (
                (f"{video.stem} " if args.prefix is None else args.prefix)
                + f"{frame.stem}"
                + (args.suffix if args.suffix is not None else f" ({position})")
            )
            destination = folder / f"{filename}{frame.suffix}"
            auto_resize_image(
                frame, destination, args.size, crop=args.crop, fill=args.fill
            )
            index += 1
            print(
                f"[{index}/{count}] {color_str(destination)} ({Resolution.from_image(destination)}) at position {position}"
            )

        print(f"🍺 {index} thumbnails extracted in {color_str(folder)}")
