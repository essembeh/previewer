import re
from pathlib import Path

from PIL import ImageFont

from .resources import fira_sans_folder


def load_fira_font(
    size: int, variant: str | None = None
) -> ImageFont.FreeTypeFont | None:
    if variant is None:
        variant = "Regular"
    ttf = fira_sans_folder / f"FiraSans-{variant}.ttf"
    if ttf.exists():
        with ttf.open("rb") as ttf_file:
            return ImageFont.truetype(ttf_file, size=size)


def list_fira_variants() -> list[str]:
    return sorted(
        map(
            lambda m: m.group("variant"),
            filter(
                None,
                map(
                    lambda f: re.fullmatch(r"FiraSans-(?P<variant>\w+).ttf", f.name),
                    filter(Path.is_file, fira_sans_folder.iterdir()),
                ),
            ),
        )
    )
