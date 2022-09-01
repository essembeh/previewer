from math import floor, log
from pathlib import Path
from subprocess import check_call, check_output
from typing import List

from .tools import TOOLS
from .utils import is_image


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
) -> List[Path]:
    """
    extract n images from a video clip usong ffmpeg
    """
    assert 0 < count < 1000, "thumbnail count must be in [1-999]"
    # compute generated filenames
    digits = floor(log(count, 10)) + 1
    generated_files = [
        folder / f"{prefix}-{i:0{digits}}.png" for i in range(1, count + 1)
    ]
    # check that none of generated file exists
    for generated_file in generated_files:
        if generated_file.exists():
            raise IOError(f"File {generated_file} already exists")
    # build the command
    fps = count / get_video_duration(video)
    command = [
        TOOLS.ffmpeg,
        "-loglevel",
        "info" if verbose else "warning",
        "-i",
        str(video),
        "-vf",
        f"fps={fps}",
        f"{folder}/{prefix}-%{digits}d.png",
    ]
    # create folder if needed
    folder.mkdir(parents=True, exist_ok=True)
    # run command
    check_call(command)
    # check generated files
    for generated_file in generated_files:
        if not is_image(generated_file):
            raise ValueError(f"Invalid generated thumbnail: {generated_file}")

    return generated_files
