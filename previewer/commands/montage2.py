"""
command line interface
"""
from argparse import ONE_OR_MORE, ArgumentParser, BooleanOptionalAction, Namespace
from operator import itemgetter
from pathlib import Path

from ..resolution import Resolution
from ..utils import color_str, is_video, iter_images_in_folder, iter_img
from ..video import iter_video_frames
from ..wand import auto_resize_img, montage


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
        help="generated filename prefix",
    )
    parser.add_argument(
        "-S",
        "--suffix",
        help="generated filename prefix",
    )
    parser.add_argument(
        "--polaroid",
        action=BooleanOptionalAction,
        help="use polaroid style",
    )
    parser.add_argument(
        "--shadow",
        action=BooleanOptionalAction,
        help="add shadow to thumbnails",
    )
    parser.add_argument(
        "--title",
        action=BooleanOptionalAction,
        default=True,
        help="add file/folder name as preview title",
    )
    parser.add_argument(
        "--filenames",
        action=BooleanOptionalAction,
        help="add filenames under thumbnails (ignored for videos)",
    )
    parser.add_argument(
        "-B",
        "--background",
        help="montage background color, list of colors: https://imagemagick.org/script/color.php",
    )
    parser.add_argument(
        "-C",
        "--columns",
        type=int,
        default=6,
        help="preview columns count (default is 6)",
    )
    parser.add_argument(
        "-R",
        "--rows",
        type=int,
        help="preview rows count",
    )
    parser.add_argument(
        "--size",
        type=Resolution,
        default=Resolution(256, 256),
        help="thumbnail size (default is 256x256)",
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
        "--offset",
        type=int,
        default=10,
        help="thumbnail offset (default is 10)",
    )
    parser.add_argument(
        "input_files",
        type=Path,
        nargs=ONE_OR_MORE,
        help="folders containing images or video files",
    )


def run(args: Namespace):
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

        if folder_or_video.is_dir():
            run_folder(args, folder_or_video, output_jpg)
        elif is_video(folder_or_video):
            run_video(args, folder_or_video, output_jpg)
        else:
            print(f"🙈 {color_str(folder_or_video)} is not a folder nor a video")


def run_folder(args: Namespace, folder: Path, output_jpg: Path):
    count = len(list(iter_images_in_folder(folder, recursive=args.recursive)))
    assert count > 0, "Folder does not contain any image"
    print(
        f"📷 Generate montage from folder {color_str(folder)} containing {count} images"
    )
    montage(
        (
            auto_resize_img(
                img,
                resolution=args.size,
                crop=args.crop,
                fill=args.fill,
            )
            for img in iter_img(iter_images_in_folder(folder, recursive=args.recursive))
        ),
        output_jpg,
        columns=args.columns,
    )
    print(f"🍺 Montage generated {color_str(output_jpg)}")


def run_video(args: Namespace, video: Path, output_jpg: Path):
    rows = args.rows or args.columns
    count = args.columns * rows
    print(f"🎬 Generate montage from video {color_str(video)} using {count} thumbnails")
    montage(
        (
            auto_resize_img(
                img,
                resolution=args.size,
                crop=args.crop,
                fill=args.fill,
            )
            for img in iter_img(
                map(itemgetter(0), iter_video_frames(video, count=args.count))
            )
        ),
        output_jpg,
        columns=args.columns,
    )
    print(f"🍺 Montage generated {color_str(output_jpg)}")
