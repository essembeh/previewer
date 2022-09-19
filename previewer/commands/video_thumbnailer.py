from argparse import ONE_OR_MORE, ArgumentParser, BooleanOptionalAction, Namespace
from datetime import timedelta
from pathlib import Path

from ..resolution import Resolution
from ..utils import auto_resize_image, check_empty_folder, check_video, color_str
from ..video import iter_video_frames


def configure(parser: ArgumentParser):
    parser.set_defaults(handler=run)

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="output folder (default is a new folder in current directory)",
    )
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        default=20,
        help="thumbnails count (default is 20)",
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
            check_empty_folder(Path(video.stem))
            if args.output is None
            else check_empty_folder(args.output)
        )

        print(f"Extract {args.count} thumbnails from {color_str(video)}")

        count = 0
        for frame, seconds in iter_video_frames(video, args.count):
            position = str(timedelta(seconds=int(seconds)))
            destination = (
                folder / f"{video.stem} {frame.stem} ({position}){frame.suffix}"
            )
            auto_resize_image(
                frame, destination, args.size, crop=args.crop, fill=args.fill
            )
            print(
                f"  {color_str(destination)} ({Resolution.from_image(destination)}) at position {position}"
            )
            count += 1

        print(f"🍺 {count} thumbnails extracted in {color_str(folder)}")
