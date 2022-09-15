"""
command line interface
"""
from argparse import ONE_OR_MORE, ArgumentParser, BooleanOptionalAction, Namespace
from operator import itemgetter
from pathlib import Path

from previewer.commands.montage import timedelta

from ..logger import DEBUG
from ..resolution import Resolution
from ..utils import color_str, is_video, iter_images_in_folder, iter_img
from ..video import get_video_duration, iter_video_frames
from ..wand import auto_resize_img, create_gif


def configure(parser: ArgumentParser):
    parser.set_defaults(handler=run)

    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="list images recursively (only for images folders)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="output folder (default is current folder)",
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
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--delay",
        type=lambda x: int(int(x) / 10),
        default=50,
        help="delay for frames in ms, default is 500",
    )
    group.add_argument(
        "--fps",
        dest="delay",
        type=lambda x: int(100 / int(x)),
        help="frame per second, default is 2",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-n",
        "--count",
        type=int,
        help="thumbnails count for videos (default calculated given --delay/--fps)",
    )
    group.add_argument(
        "--speed",
        type=int,
        help="calculate frames count to extract to respect given speed (only for videos)",
    )
    parser.add_argument(
        "--colors",
        type=int,
        default=256,
        help="gif colors",
    )
    parser.add_argument(
        "--size",
        type=Resolution,
        default=Resolution(640, 480),
        help="thumbnail size (default is 640x480)",
    )
    parser.add_argument(
        "--crop",
        action=BooleanOptionalAction,
        default=False,
        help="crop thumbnails",
    )
    parser.add_argument(
        "--fill",
        action=BooleanOptionalAction,
        default=False,
        help="fill thumbnails",
    )
    parser.add_argument(
        "input_files",
        type=Path,
        nargs=ONE_OR_MORE,
        help="folders containing images or video files",
    )


def run(args: Namespace):
    for folder_or_video in args.input_files:
        output_gif = (
            (args.output or Path())
            / f"{args.prefix or ''}{folder_or_video.name if folder_or_video.is_dir() else folder_or_video.stem}{args.suffix or ''}.gif"
        )
        if output_gif.exists():
            print(
                f"💡 Gif {color_str(output_gif)} already generated from {color_str(folder_or_video)}"
            )
            continue

        if folder_or_video.is_dir():
            run_folder(args, folder_or_video, output_gif)
        elif is_video(folder_or_video):
            run_video(args, folder_or_video, output_gif)
        else:
            print(f"🙈 {color_str(folder_or_video)} is not a folder nor a video")


def run_folder(args: Namespace, folder: Path, output_gif: Path):
    count = len(list(iter_images_in_folder(folder, recursive=args.recursive)))
    assert count > 0, "Folder does not contain any image"

    print(f"📷 Generate Gif from folder {color_str(folder)} containing {count} images")
    create_gif(
        (
            auto_resize_img(
                img,
                resolution=args.size,
                crop=args.crop,
                fill=args.fill,
            )
            for img in iter_img(iter_images_in_folder(folder, recursive=args.recursive))
        ),
        output_gif,
        delay=args.delay,
    )
    print(f"🍺 Gif generated {output_gif}")


def run_video(args: Namespace, video: Path, output_gif: Path):
    # compute frame count if needed
    count = args.count
    if count is None:
        duration = get_video_duration(video)
        count = int(duration * (100 / args.delay))
        if args.speed is not None:
            count = int(count / args.speed)
        DEBUG(
            "Video duration is %s, extract %d frames, gif duration will be %s",
            timedelta(seconds=duration),
            count,
            timedelta(milliseconds=count * args.delay * 10),
        )

    print(f"🎬 Generate Gif from video {color_str(video)} using {count} thumbnails")
    create_gif(
        (
            auto_resize_img(
                img,
                resolution=args.size,
                crop=args.crop,
                fill=args.fill,
            )
            for img in iter_img(map(itemgetter(0), iter_video_frames(video, count)))
        ),
        output_gif,
        delay=args.delay,
    )
    print(f"🍺 Gif generated {output_gif}")
