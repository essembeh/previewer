import shlex
from dataclasses import dataclass
from pathlib import Path
from subprocess import check_call
from typing import Iterable, Optional

from .logger import DEBUG
from .resolution import Resolution
from .tools import TOOLS
from .utils import check_image


@dataclass
class Montage:
    auto_orient: bool = True
    background: Optional[str] = None
    columns: int = 6
    polaroid: bool = False
    shadow: bool = True
    th_offset: int = 0
    th_size: Optional[Resolution] = None
    font: Optional[str] = None

    def build(
        self,
        images: Iterable[Path],
        output_jpg: Path,
        filenames: bool = False,
        title: Optional[str] = None,
    ) -> str:

        images_args = [str(i) for i in images]

        command = [
            TOOLS.montage,
            "-tile",
            self.columns if len(images_args) > self.columns else len(images_args),
        ]
        if self.th_size is None:
            command += [
                "-geometry",
                f"+{self.th_offset}+{self.th_offset}",
            ]
        else:
            command += [
                "-geometry",
                f"{self.th_size}^+{self.th_offset}+{self.th_offset}",
            ]

        if title is not None:
            command += ["-title", title]
        if filenames:
            # doc: https://imagemagick.org/script/escape.php
            command += ["-label", r"%t"]
        if self.background:
            command += ["-background", self.background]
        if self.auto_orient:
            command.append("-auto-orient")
        if self.polaroid:
            command.append("+polaroid")
        if self.shadow:
            command += ["-shadow"]
        if self.font is not None:
            command += ["-font", self.font]
        command += images_args
        command.append(output_jpg)

        command = [str(x) for x in command]
        command_str = shlex.join(command)
        DEBUG("montage command: %s", command_str)
        assert not output_jpg.exists()
        output_jpg.parent.mkdir(parents=True, exist_ok=True)
        check_call(command)
        check_image(output_jpg)
        return command_str
