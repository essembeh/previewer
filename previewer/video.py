import shlex
from pathlib import Path
from subprocess import check_call, check_output

from .tools import TOOLS


def get_video_duration(video: Path) -> float:
    """
    use mediainfo to get the video duration as float
    """
    command = [TOOLS.mediainfo, "--Inform=General;%Duration%", video]
    text = check_output(list(map(str, command)))
    duration_ms = float(text)
    assert duration_ms > 0
    return duration_ms / 1000


def extract_images(
    video: Path, folder: Path, count: int, prefix: str = "out", verbose: bool = True
) -> str:
    """
    extract n images from a video clip usong ffmpeg
    """
    fps = count / get_video_duration(video)
    command = [
        TOOLS.ffmpeg,
        "-loglevel",
        "info" if verbose else "warning",
        "-i",
        str(video),
        "-vf",
        f"fps={fps}",
        f"{folder}/{prefix}-%3d.png",
    ]
    check_call(command)
    return shlex.join(command)
