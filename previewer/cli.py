"""
command line interface
"""

import traceback
from argparse import ONE_OR_MORE, ArgumentParser
from os import getenv
from pathlib import Path
from tempfile import TemporaryDirectory

from . import __version__
from .montage import Montage
from .utils import color_str, copy_and_resize_images, is_video, iter_images
from .video import extract_images


def video_thumbnailer():
    """
    entry point
    """
    parser = ArgumentParser(description="extract thumbnails from video")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("--verbose", action="store_true", help="print more information")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path.cwd(),
        help="output folder, default is current folder",
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        required=True,
        help="thumbnails count (must be between 1-999)",
    )
    parser.add_argument("--prefix", help="prefix for thumbnails")
    parser.add_argument("video", nargs=1, type=Path, help="video file")
    args = parser.parse_args()

    assert 0 < args.count < 1000

    args.output.mkdir(parents=True, exist_ok=True)
    video = args.video[0]
    prefix = args.prefix or video.stem

    print(
        f"Extract {args.count} thumbnails from {color_str(video)} to {color_str(args.output)}"
    )
    extract_images(video, args.output, args.count, prefix=prefix, verbose=args.verbose)
    print("🍺 Done")


def previewer():
    """
    entry point
    """
    parser = ArgumentParser(description="extract thumbnails from video")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "-P",
        "--polaroid",
        action="store_true",
        help="use polaroid style",
    )
    parser.add_argument(
        "-T",
        "--no-title",
        action="store_false",
        dest="title",
        help="do not add title to the preview",
    )
    parser.add_argument(
        "-L",
        "--filename",
        action="store_true",
        help="add filename as label (only for images folders)",
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
        help="preview rows count (only for video files)",
    )
    parser.add_argument(
        "-s",
        "--size",
        type=int,
        default=256,
        help="thumbnail size (default is 256)",
    )
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
        default=Path("."),
        help="output folder (default is current folder)",
    )
    parser.add_argument(
        "--suffix",
        default="preview",
        help="preview filename suffix (default is 'preview')",
    )
    parser.add_argument(
        "folder_or_video",
        type=Path,
        nargs=ONE_OR_MORE,
        help="folder containing images or video file",
    )
    args = parser.parse_args()

    montage = Montage(
        background=args.background,
        columns=args.columns,
        th_size=args.size,
        polaroid=args.polaroid,
    )

    for folder_or_video in args.folder_or_video:
        output_jpg = (
            args.output
            / f"{folder_or_video.stem}{'-' if args.suffix else ''}{args.suffix or ''}.jpg"
        )
        if output_jpg.exists():
            print(
                f"💡 Preview {color_str(output_jpg)} already generated from {color_str(folder_or_video)}"
            )
            continue

        try:
            with TemporaryDirectory() as tmp:
                tmp_folder = Path(tmp)

                if folder_or_video.is_dir():
                    images = list(
                        iter_images(folder_or_video, recursive=args.recursive)
                    )
                    assert len(images) > 0, "Folder does not contain any image"
                    print(
                        f"📷 Generate preview {color_str(output_jpg)} from folder {color_str(folder_or_video)} ({len(images)} images)"
                    )
                    montage.build(
                        copy_and_resize_images(
                            folder_or_video, images, tmp_folder, montage.th_size
                        ),
                        output_jpg,
                        filename=args.filename,
                        title=folder_or_video.name if args.title else None,
                    )
                elif is_video(folder_or_video):
                    rows = args.rows or args.columns
                    count = args.columns * rows
                    print(
                        f"🎬 Generate preview {color_str(output_jpg)} from video {color_str(folder_or_video)} ({count} thumbnails)"
                    )
                    extract_images(
                        folder_or_video,
                        tmp_folder,
                        count,
                        verbose=False,
                    )
                    montage.build(
                        iter_images(tmp_folder),
                        output_jpg,
                        title=folder_or_video.name if args.title else None,
                    )
                else:
                    print(f"🙈 {color_str(folder_or_video)} is not a folder nor a video")
        except BaseException as error:  # pylint: disable=broad-except
            print(
                f"💥 Cannot generate preview for {color_str(folder_or_video)}: {color_str(error)}"
            )
            if getenv("DEBUG") == "1":
                traceback.print_exc()
