from datetime import timedelta
from math import floor, log
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator, Optional

from PIL import Image, ImageDraw

from .font import load_fira_font
from .mime import check_image, is_image
from .video import extract_frame, get_video_duration


def collect_folder_images(folder: Path, recursive: bool = False) -> list[Path]:
    assert folder.is_dir()
    out = sorted(filter(is_image, folder.iterdir()), key=lambda f: f.name.lower())
    if recursive:
        for subfolder in sorted(
            filter(Path.is_dir, folder.iterdir()), key=lambda f: f.name.lower()
        ):
            out += collect_folder_images(subfolder, recursive=recursive)
    return out


def iter_video_frames(
    video: Path,
    count: int,
    start: Optional[float] = None,
    end: Optional[float] = None,
    extension: str = "jpg",
) -> Iterator[tuple[Path, float]]:
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
            yield check_image(
                extract_frame(
                    video,
                    folder / f"{(index+1):0{digits}}.{extension}",
                    seconds=seconds,
                )
            ), seconds


def insert_timestamp(
    image: Image.Image, ts: float, font_variant: str = "Regular", shadow: bool = True
) -> Image.Image:
    font = load_fira_font(int(image.height / 10), variant=font_variant)
    if font is not None:
        text = str(timedelta(seconds=int(ts)))
        text_size = font.getbbox(text)[2:]
        draw = ImageDraw.Draw(image)
        x, y = int(image.width * 0.01), int(image.height * 0.98 - text_size[1])
        if shadow:
            draw.text(
                (int(x + text_size[1] / 12), int(y + text_size[1] / 12)),
                text,
                fill="black",
                font=font,
            )
        draw.text((x, y), text, fill="white", font=font)
    return image
