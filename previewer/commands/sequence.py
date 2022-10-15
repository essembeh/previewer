"""
command line interface
"""
from argparse import ONE_OR_MORE, ArgumentParser, Namespace
from datetime import timedelta
from operator import itemgetter
from pathlib import Path

from ..logger import DEBUG
from ..tools.resizer import ImageResizer
from ..tools.sequence import create_sequence
from ..utils import color_str, is_video, iter_images_in_folder, iter_img
from ..video import Position, get_video_duration, iter_video_frames
from .utils import add_geometry_group, get_image_resizer, parser_group


def configure(parser: ArgumentParser):
    parser.set_defaults(handler=run)

    ## Generated file
    with parser_group(parser, name="output file options") as group:
        group.add_argument(
            "-o",
            "--output",
            type=Path,
            metavar="FOLDER",
            help="output folder (default is current folder)",
        )
        group.add_argument(
            "-P",
            "--prefix",
            help="generated filename prefix",
        )
        group.add_argument(
            "-S",
            "--suffix",
            help="generated filename suffix",
        )
        group.add_argument(
            "--format",
            dest="extension",
            choices=["gif", "webm", "webp", "mp4"],
            default="gif",
            help="generated file format, default is gif",
        )

    ## Geometry
    add_geometry_group(parser, resolution_required=False, crop_default=True)

    ## Video only
    with parser_group(parser, name="only for videos") as group:
        group.add_argument(
            "--start",
            type=Position,
            metavar="POSITION",
            default="5%",
            help="start position (default: 5%%)",
        )
        with parser_group(parser, exclusive=True) as xgroup:
            xgroup.add_argument(
                "--end",
                type=Position,
                metavar="POSITION",
                default="-5%",
                help="end position (default: -5%%)",
            )
            xgroup.add_argument(
                "--duration",
                type=Position,
                metavar="DURATION",
                help="calculate --end given the length",
            )
        with parser_group(parser, exclusive=True) as xgroup:
            xgroup.add_argument(
                "-n",
                "--count",
                type=int,
                help="number of frames to extract (default calculated given --delay/--fps)",
            )
            xgroup.add_argument(
                "--speed",
                type=int,
                metavar="INT",
                help="calculate frames count to extract to respect given speed",
            )

    ## Folder only
    with parser_group(parser, name="only for folders") as group:
        group.add_argument(
            "--shuffle",
            action="store_true",
            help="shuffle image order, default is alphabetical order",
        )
        group.add_argument(
            "-r",
            "--recursive",
            action="store_true",
            help="list images recursively",
        )

    with parser_group(parser, exclusive=True) as xgroup:
        xgroup.add_argument(
            "--delay",
            type=int,
            default=500,
            metavar="MILLISECONDS",
            help="delay for frames in ms, default is 500",
        )
        xgroup.add_argument(
            "--fps",
            type=int,
            metavar="INT",
            help="frames per second",
        )
    with parser_group(parser, exclusive=True) as xgroup:
        xgroup.add_argument(
            "--aba",
            action="store_const",
            dest="aba",
            const="aba",
            help="create an A-B-A sequence",
        )
        xgroup.add_argument(
            "--abba",
            action="store_const",
            dest="aba",
            const="abba",
            help="create an A-B-B-A sequence",
        )

    parser.add_argument(
        "input_files",
        type=Path,
        nargs=ONE_OR_MORE,
        help="folders containing images or video files",
    )


def run(args: Namespace):
    resizer = get_image_resizer(args)
    for folder_or_video in args.input_files:
        output_file = (
            (args.output or Path())
            / f"{args.prefix or ''}{folder_or_video.name if folder_or_video.is_dir() else folder_or_video.stem}{args.suffix or ''}.{args.extension}"
        )
        if output_file.exists():
            print(
                f"💡 Sequence {color_str(output_file)} already generated from {color_str(folder_or_video)}"
            )
            continue

        if folder_or_video.is_dir():
            run_folder(args, folder_or_video, output_file, resizer)
        elif is_video(folder_or_video):
            run_video(args, folder_or_video, output_file, resizer)
        else:
            print(f"🙈 {color_str(folder_or_video)} is not a folder nor a video")


def run_folder(args: Namespace, folder: Path, output_file: Path, resizer: ImageResizer):
    count = len(list(iter_images_in_folder(folder, recursive=args.recursive)))
    assert count > 0, "Folder does not contain any image"

    print(
        f"📷 Generate {args.extension} from folder {color_str(folder)} containing {count} images"
    )
    create_sequence(
        map(
            resizer.transform,
            iter_img(
                iter_images_in_folder(
                    folder, recursive=args.recursive, shuffle=args.shuffle
                )
            ),
        ),
        output_file,
        delay=int(100 / args.fps if args.fps else args.delay / 10),
        aba_loop=args.aba,
        gif_optimize=args.extension == "gif",
    )
    print(f"🍺 Sequence generated {color_str(output_file)}")


def run_video(args: Namespace, video: Path, output_file: Path, resizer: ImageResizer):
    duration = get_video_duration(video)
    start = args.start.get_seconds(duration)
    end = end = (
        start + args.duration.get_seconds(duration)
        if args.duration is not None
        else args.end.get_seconds(duration)
    )
    count = args.count or int(
        (end - start) * args.fps if args.fps else (end - start) * (1000 / args.delay)
    )
    if args.speed is not None:
        count = int(count / args.speed)
    DEBUG(
        "Video duration is %s, extract %d frames from %.3lf -> %.3lf, gif duration will be %s",
        timedelta(seconds=duration),
        count,
        start,
        end,
        timedelta(milliseconds=count * args.delay * 10),
    )

    print(
        f"🎬 Generate {args.extension} from video {color_str(video)} using {count} thumbnails"
    )
    create_sequence(
        map(
            resizer.transform,
            iter_img(
                map(
                    itemgetter(0), iter_video_frames(video, count, start=start, end=end)
                )
            ),
        ),
        output_file,
        delay=int(100 / args.fps if args.fps else args.delay / 10),
        aba_loop=args.aba,
        gif_optimize=args.extension == "gif",
    )
    print(f"🍺 Sequence generated {color_str(output_file)}")
