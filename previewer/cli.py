"""
command line interface
"""

import traceback
from argparse import ONE_OR_MORE, ArgumentParser, BooleanOptionalAction
from os import getenv
from pathlib import Path
from tempfile import TemporaryDirectory

from colorama import Fore

from . import __version__
from .montage import Montage
from .utils import color_str, copy_and_resize_images, is_video, iter_images
from .video import extract_images, get_video_duration


def folder_thumbnailer():
    """
    entry point
    """
    parser = ArgumentParser(description="extract thumbnails from folder")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("."),
        help="output folder, default is current folder",
    )
    parser.add_argument(
        "-s",
        "--size",
        type=int,
        default=256,
        help="thumbnails max size (default is 256)",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="list images recursively (only for images folders)",
    )
    parser.add_argument("folder", nargs=1, type=Path, help="folder containing images")
    args = parser.parse_args()

    try:
        folder = args.folder[0]
        assert folder.is_dir(), f"Invalid folder: {folder}"

        images = list(iter_images(folder, recursive=args.recursive))
        assert len(images) > 0, f"Folder {folder} does not contain any image"

        print(
            f"📷 Generate {len(images)} thumbnails from {color_str(folder)} to {color_str(args.output)}"
        )
        for image, resized_image in copy_and_resize_images(
            folder, images, args.output, args.size
        ):
            print(f"  {color_str(image)} -> {color_str(resized_image)}")
    except KeyboardInterrupt:  # pylint: disable=broad-except
        print("❌ Process interrupted")
        exit(1)
    except BaseException as error:  # pylint: disable=broad-except
        print(f"💥 Cannot generate thumbnails: {color_str(error)}")
        if getenv("DEBUG") == "1":
            traceback.print_exc()


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
        default=Path("."),
        help="output folder, default is current folder",
    )
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        help="thumbnails count (default is 1 per second)",
    )
    parser.add_argument("--prefix", help="prefix for thumbnails")
    parser.add_argument("video", nargs=1, type=Path, help="video file")
    args = parser.parse_args()

    try:
        video = args.video[0]
        assert is_video(video), f"Invalid video: ${video}"
        # compute thumbnails count
        count = args.count or int(get_video_duration(video)) or 1
        prefix = args.prefix or video.stem
        args.output.mkdir(parents=True, exist_ok=True)
        print(
            f"Extract {args.count} thumbnails from {color_str(video)} to {color_str(args.output)}"
        )
        images = extract_images(
            video, args.output, count, prefix=prefix, verbose=args.verbose
        )
        for image in images:
            print(f"  {color_str(image)}")
        print(f"🍺 {len(images)} thumbnails generated")
    except KeyboardInterrupt:  # pylint: disable=broad-except
        print("❌ Process interrupted")
        exit(1)
    except BaseException as error:  # pylint: disable=broad-except
        print(f"💥 Cannot generate thumbnails: {color_str(error)}")
        if getenv("DEBUG") == "1":
            traceback.print_exc()


def previewer():
    """
    entry point
    """
    parser = ArgumentParser(description="extract thumbnails from video")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("--verbose", action="store_true", help="print more information")
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
        "--auto_orient",
        action=BooleanOptionalAction,
        help="auto orient thumbnails",
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
        type=int,
        default=256,
        help="thumbnail size (default is 256)",
    )
    parser.add_argument(
        "--offset",
        type=int,
        default=10,
        help="thumbnail offset (default is 10)",
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
        default=" preview",
        help="preview filename suffix (default is ' preview')",
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
        th_offset=args.offset,
    )
    if args.polaroid is not None:
        montage.polaroid = args.polaroid
    if args.shadow is not None:
        montage.shadow = args.shadow
    if args.auto_orient is not None:
        montage.auto_orient = args.auto_orient

    for folder_or_video in args.folder_or_video:
        output_jpg = args.output / f"{folder_or_video.stem}{args.suffix or ''}.jpg"
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
                    resized_images = []
                    for _image, resized_image in copy_and_resize_images(
                        folder_or_video, images, tmp_folder, montage.th_size
                    ):
                        resized_images.append(resized_image)
                    command = montage.build(
                        resized_images,
                        output_jpg,
                        filenames=args.filenames,
                        title=folder_or_video.name if args.title else None,
                    )
                    if args.verbose:
                        print(f"{Fore.YELLOW}{command}{Fore.RESET}")
                elif is_video(folder_or_video):
                    rows = args.rows or args.columns
                    count = args.columns * rows
                    print(
                        f"🎬 Generate preview {color_str(output_jpg)} from video {color_str(folder_or_video)} ({count} thumbnails)"
                    )
                    images = extract_images(
                        folder_or_video,
                        tmp_folder,
                        count,
                        verbose=False,
                    )
                    command = montage.build(
                        images,
                        output_jpg,
                        title=folder_or_video.name if args.title else None,
                    )
                    if args.verbose:
                        print(f"{Fore.YELLOW}{command}{Fore.RESET}")
                else:
                    print(f"🙈 {color_str(folder_or_video)} is not a folder nor a video")
        except KeyboardInterrupt:  # pylint: disable=broad-except
            print("❌ Process interrupted")
            if output_jpg.exists():
                output_jpg.unlink()
            exit(1)
        except BaseException as error:  # pylint: disable=broad-except
            print(
                f"💥 Cannot generate preview for {color_str(folder_or_video)}: {color_str(error)}"
            )
            if getenv("DEBUG") == "1":
                traceback.print_exc()
            if output_jpg.exists():
                output_jpg.unlink()
