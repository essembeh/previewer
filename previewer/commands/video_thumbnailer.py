from argparse import ONE_OR_MORE, ArgumentParser, BooleanOptionalAction, Namespace
from datetime import timedelta
from pathlib import Path

from ..resolution import Resolution
from ..utils import auto_resize_image, check_empty_folder, check_video, color_str
from ..video import get_video_duration, iter_video_frames, position_to_seconds


def configure(parser: ArgumentParser):
    parser.set_defaults(handler=run)

    parser.add_argument(
        "-P",
        "--prefix",
        type=str,
        help="generated filename prefix (default is video filename)",
    )
    parser.add_argument(
        "-S",
        "--suffix",
        type=str,
        help="generated filename prefix (default frame time)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="output folder (default is a new folder in current directory)",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--fps",
        type=int,
        help="frames per second",
    )
    group.add_argument(
        "-n",
        "--count",
        type=int,
        default=20,
        help="thumbnails count (default is 20)",
    )
    parser.add_argument(
        "--start",
        type=position_to_seconds,
        metavar="SECONDS.MILLISECONDS",
        help="start position",
    )
    parser.add_argument(
        "--end",
        type=position_to_seconds,
        metavar="SECONDS.MILLISECONDS",
        help="end position",
    )
    parser.add_argument(
        "--size",
        type=Resolution,
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
    parser.add_argument("videos", nargs=ONE_OR_MORE, type=Path, help="video file")


def run(args: Namespace):
    for video in args.videos:
        video = check_video(video)
        folder = (
            check_empty_folder(args.output)
            if args.output is not None
            else check_empty_folder(Path(video.stem))
        )
        duration = get_video_duration(video)
        start, end = args.start or 0, args.end or int(duration)
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
