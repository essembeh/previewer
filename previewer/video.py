"""
Video related utility functions
"""
import json
import subprocess
from dataclasses import dataclass
from datetime import timedelta
from os import getenv
from pathlib import Path
from re import fullmatch
from typing import List

_POSITION_PATTERN = r"(?P<minus>-)?((((?P<hours>[0-9]{1,2}):)?(?P<minutes>[0-6]?[0-9]):)?(?P<seconds>[0-6]?[0-9](\.[0-9]{1,3})?)|(?P<seconds_only>[0-9]+(\.[0-9]{1,3})?)|(?P<percent>(100|[0-9]{1,2}))%)"


@dataclass
class Position:
    expression: str

    def get_seconds(self, duration: float) -> float:
        matcher = fullmatch(_POSITION_PATTERN, self.expression)
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
    command = [
        getenv("FFPROBE_BIN", "ffprobe"),
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
    stdout = subprocess.check_output(command)
    return float(stdout)


def get_video_metadata(video: Path) -> dict:
    command = [
        getenv("FFPROBE_BIN", "ffprobe"),
        "-loglevel",
        "0",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        "-i",
        str(video),
    ]
    stdout = subprocess.check_output(command)
    return json.loads(stdout)


def extract_frame(video: Path, output: Path, seconds: float) -> Path:
    """
    Extract a single frame from a video
    """
    if output.exists():
        raise FileExistsError(f"File already exists: {output}")

    command = [
        getenv("FFMPEG_BIN", "ffmpeg"),
        "-ss",
        str(seconds),
        "-i",
        str(video),
        "-frames:v",
        "1",
        str(output),
    ]
    subprocess.check_call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output


def get_video_description(video: Path) -> List[str]:
    metadata = get_video_metadata(video)
    return [
        f"File: {video.name}",
        f"Size: {video.stat().st_size} bytes",
        f"Duration: {timedelta(seconds=float(metadata['format']['duration']))}",
    ]
