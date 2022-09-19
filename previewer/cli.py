"""
command line interface
"""

from argparse import ArgumentParser

from . import __version__
from .commands import gif, montage, montage2, resize, video_thumbnailer
from .logger import logger, logging
from .utils import color_str


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

    subparsers = parser.add_subparsers()
    video_thumbnailer(
        subparsers.add_parser(
            "video-thumbnailer",
            aliases=["vt"],
            help="extract thumbnails from video clips",
        )
    )
    montage(
        subparsers.add_parser(
            "montage",
            help="build an image with thumbnails from a video clip or a folder",
        )
    )
    gif(
        subparsers.add_parser(
            "gif",
            help="build a gif with thumbnails from a video clip or a folder",
        )
    )
    resize(
        subparsers.add_parser(
            "resize",
            help="resize given images",
        )
    )
    ## WIP commands
    montage2(
        subparsers.add_parser(
            "montage2", help="work-in-progress replacement of montage subcommand"
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
