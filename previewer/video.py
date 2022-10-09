"""
Video related utility functions
"""
import time
from dataclasses import dataclass
from datetime import timedelta
from math import floor, log
from pathlib import Path
from re import fullmatch
from subprocess import DEVNULL
from tempfile import TemporaryDirectory
from typing import Iterator, Optional, Tuple

from .external import FF_MPEG, FF_PROBE
from .logger import DEBUG
from .utils import check_image

PATTERN = r"(?P<minus>-)?((((?P<hours>[0-9]{1,2}):)?(?P<minutes>[0-6]?[0-9]):)?(?P<seconds>[0-6]?[0-9](\.[0-9]{1,3})?)|(?P<seconds_only>[0-9]+(\.[0-9]{1,3})?)|(?P<percent>(100|[0-9]{1,2}))%)"


@dataclass
class Position:
    expression: str

    def get_seconds(self, duration: float) -> float:
        matcher = fullmatch(PATTERN, self.expression)
        assert matcher is not None, f"Cannot parse {self.expression}"

        if matcher.group("percent") is not None:
            out = duration * int(matcher.group("percent")) / 100
        elif matcher.group("seconds_only") is not None:
            out = float(matcher.group("seconds_only"))
        else:
            out = float(matcher.group("seconds"))
            if matcher.group("minutes"):
                out += int(matcher.group("minutes")) * 60
                if matcher.group("hours"):
                    out += int(matcher.group("hours")) * 3600
        if matcher.group("minus") is not None:
            out = duration - out
        assert 0 <= out <= duration, f"Invalid position {self.expression}"
        return out


def get_video_duration(video: Path) -> float:
    """
    use ffprobe to get the video duration as float
    """
    with FF_PROBE.new_command() as cmd:
        cmd += [
            "-i",
            video,
            "-v",
            "quiet",
            "-show_entries",
            "format=duration",
            "-hide_banner",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
        ]
        return float(cmd.check_output())


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

    with FF_MPEG.new_command() as cmd:
        cmd += ["-ss", seconds, "-i", video, "-frames:v", "1", output]
        # run command
        start = time.time()
        cmd.check_call(stdout=DEVNULL, stderr=DEVNULL)
        DEBUG("Frame %s extracted in %.3lf sec", output, time.time() - start)

    return check_image(output)
