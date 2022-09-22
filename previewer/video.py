"""
Video related utility functions
"""
import time
from datetime import timedelta
from math import floor, log
from pathlib import Path
from re import fullmatch
from subprocess import DEVNULL, check_call, check_output
from tempfile import TemporaryDirectory
from typing import Iterator, Optional, Tuple

from .logger import DEBUG
from .tools import TOOLS
from .utils import check_image


def position_to_seconds(text: str) -> float:
    """
    Parse a duration and return the secods count as float
    Valid formats are
        1234
        1234.1
        1234.12
        1234.123
        12:34
        12:34.1
        12:34.12
        12:34.123
        1:23:45
        1:23:45.1
        1:23:45.12
        1:23:45.123
    """
    pattern = r"(((?P<hours>[0-9]):)?(?P<minutes>[0-6]?[0-9]):)?(?P<seconds>[0-6]?[0-9](\.[0-9]{1,3})?)"
    matcher = fullmatch(pattern, text)
    if matcher is None:
        out = float(text)
    else:
        out = float(matcher.group("seconds"))
        if matcher.group("minutes"):
            out += int(matcher.group("minutes")) * 60
            if matcher.group("hours"):
                out += int(matcher.group("hours")) * 3600
    return out


def get_video_duration(video: Path) -> float:
    """
    use ffprobe to get the video duration as float
    """
    text = check_output(
        [
            TOOLS.ffprobe,
            "-i",
            str(video),
            "-v",
            "quiet",
            "-show_entries",
            "format=duration",
            "-hide_banner",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
        ]
    )
    return float(text)


def iter_video_frames(
    video: Path,
    count: int,
    start: Optional[float] = None,
    end: Optional[float] = None,
    extension: str = "jpg",
) -> Iterator[Tuple[Path, float]]:
    """
    Iterate over given number of frames from a video
    """
    duration = get_video_duration(video)
    start = 0 if start is None else start
    end = int(duration) if end is None else end

    assert (
        0 <= start < end <= duration
    ), f"Invalid start ({start}) or end ({end}) position, must be [0-{duration:.3f}]"

    step = 0 if count == 1 else (end - start) / (count - 1)
    digits = floor(log(count, 10)) + 1

    with TemporaryDirectory() as tmp:
        folder = Path(tmp)
        for index in range(0, count):
            seconds = start + index * step
            DEBUG(
                "extract frame %d/%d at position %s",
                index + 1,
                count,
                timedelta(seconds=seconds),
            )
            yield extract_frame(
                video,
                folder / f"{(index+1):0{digits}}.{extension}",
                seconds=seconds,
            ), seconds


def extract_frame(video: Path, output: Path, seconds: float) -> Path:
    """
    Extract a single frame from a video
    """
    if output.exists():
        raise FileExistsError(f"File already exists: {output}")
    # prepare command
    command = [
        TOOLS.ffmpeg,
        "-ss",
        f"{seconds}",
        "-i",
        str(video),
        "-frames:v",
        "1",
        str(output),
    ]
    # run command
    start = time.time()
    check_call(command, stdout=DEVNULL, stderr=DEVNULL)
    DEBUG("Frame %s extracted in %.3lf sec", output, time.time() - start)

    return check_image(output)
