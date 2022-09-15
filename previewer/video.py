from datetime import timedelta
from math import floor, log
from pathlib import Path
from subprocess import DEVNULL, check_call, check_output
from tempfile import TemporaryDirectory
from typing import Iterator, Tuple

from .logger import DEBUG
from .tools import TOOLS
from .utils import check_image


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
    extension: str = "jpg",
) -> Iterator[Tuple[Path, float]]:
    """
    Iterate over given number of frames from a video
    """
    duration = get_video_duration(video)
    delta = duration / (count + 1)
    digits = floor(log(count, 10)) + 1

    with TemporaryDirectory() as tmp:
        folder = Path(tmp)
        for index in range(1, count + 1):
            seconds = index * delta
            DEBUG(
                "extract frame %d/%d at position %s",
                index,
                count,
                timedelta(seconds=seconds),
            )
            yield extract_frame(
                video,
                folder / f"{index:0{digits}}.{extension}",
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
    check_call(command, stdout=DEVNULL, stderr=DEVNULL)

    return check_image(output)
