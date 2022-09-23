"""
command line interface
"""

import logging
from argparse import ArgumentParser

from previewer.wand import DEFAULT_BLUR

from . import __version__
from .commands import montage, resize, sequence, video_thumbnailer
from .logger import DEBUG, logger
from .utils import color_str


def configure_blur(text: str):
    values = text.split(":")
    assert len(values) == 4
    if len(values[0]) > 0:
        DEFAULT_BLUR.blur_sigma = float(values[0])
    if len(values[1]) > 0:
        DEFAULT_BLUR.black = float(values[1])
    if len(values[2]) > 0:
        DEFAULT_BLUR.white = float(values[2])
    if len(values[3]) > 0:
        DEFAULT_BLUR.gamma = float(values[3])
    DEBUG("Configured blur: %s", DEFAULT_BLUR)
    return values


def run():
    """
    entry point
    """
    parser = ArgumentParser(description="preview/thumbnails generator")

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    logger_group = parser.add_mutually_exclusive_group()
    logger_group.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        dest="logger_level",
        const=logging.DEBUG,
        default=logging.INFO,
        help="print more information",
    )
    logger_group.add_argument(
        "-q",
        "--quiet",
        action="store_const",
        dest="logger_level",
        const=logging.WARNING,
        help="print less information",
    )

    parser.add_argument(
        "--blur",
        type=configure_blur,
        help="blur option, format 'sigma:black:white:gamma' (float:float:float:float), "
        + f"default is {DEFAULT_BLUR.blur_sigma}:{DEFAULT_BLUR.black}:{DEFAULT_BLUR.white}:{DEFAULT_BLUR.gamma}",
    )
    subparsers = parser.add_subparsers()
    video_thumbnailer(
        subparsers.add_parser(
            "frames",
            aliases=["video-thumbnailer", "vt"],
            help="extract thumbnails from video clips",
        )
    )
    montage(
        subparsers.add_parser(
            "montage",
            help="build an image with thumbnails from a video clip or a folder",
        )
    )
    sequence(
        subparsers.add_parser(
            "sequence",
            aliases=["gif"],
            help="build a sequence (gif or video) with thumbnails from a video clip or a folder",
        )
    )
    resize(
        subparsers.add_parser(
            "resize",
            help="resize given images",
        )
    )

    args = parser.parse_args()

    logger.setLevel(args.logger_level)

    if "handler" not in args:
        parser.print_usage()
    else:
        try:
            args.handler(args)
        except KeyboardInterrupt:
            print("❌ Process interrupted")
            exit(1)
        except BaseException as error:  # pylint: disable=broad-except
            print(f"💥 Error: {color_str(error)}")
            if args.logger_level == logging.DEBUG:
                logger.exception("Exception", exc_info=error)
