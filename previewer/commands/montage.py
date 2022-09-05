"""
command line interface
"""

import traceback
from argparse import ONE_OR_MORE, ArgumentParser, BooleanOptionalAction
from os import getenv
from pathlib import Path
from tempfile import TemporaryDirectory

from colorama import Fore

from .. import __version__
from ..montage import Montage
from ..resolution import Resolution
from ..utils import color_str, copy_and_resize_images, is_video, iter_images
from ..video import extract_images


def run():
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
        type=Resolution,
        default=Resolution(256, 256),
        help="thumbnail size (default is 256x256)",
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
