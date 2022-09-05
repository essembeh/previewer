"""
command line interface
"""

import shutil
import traceback
from argparse import ArgumentParser
from os import getenv
from pathlib import Path

from .. import __version__
from ..resolution import Resolution
from ..utils import color_str, is_video, resize_image
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
        action="store_true",
        help="crop thumbnails",
    )
    parser.add_argument(
        "--prefix", help="prefix for thumbnails (default is video filename)"
    )
    parser.add_argument("video", nargs=1, type=Path, help="video file")
    args = parser.parse_args()

    try:
        video = args.video[0]
        assert is_video(video), f"Invalid video: {video}"
        args.output.mkdir(parents=True, exist_ok=True)
        print(
            f"Extract {args.count} thumbnails from {color_str(video)} to {color_str(args.output)}"
        )
        images = extract_images(
            video,
            args.output,
            args.count,
            prefix=args.prefix or video.stem,
            verbose=args.verbose,
        )
        for image in images:
            if args.size is None:
                print(f"  {color_str(image)}")
            else:
                tmp = resize_image(
                    image,
                    image.parent / f"temp-{image.name}",
                    args.size,
                    crop=args.crop,
                )
                shutil.move(tmp, image)
                print(f"  {color_str(image)} ({args.size})")
        print(f"🍺 {len(images)} thumbnails generated")
    except KeyboardInterrupt:  # pylint: disable=broad-except
        print("❌ Process interrupted")
        exit(1)
    except BaseException as error:  # pylint: disable=broad-except
        print(f"💥 Cannot generate thumbnails: {color_str(error)}")
        if getenv("DEBUG") == "1":
            traceback.print_exc()
