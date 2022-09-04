import shlex
from dataclasses import dataclass
from pathlib import Path
from subprocess import check_call
from typing import Iterable, Optional

from .resolution import Resolution
from .tools import TOOLS


@dataclass
class Montage:
    background: Optional[str] = None
    th_size: Resolution = Resolution(256, 256)
    th_offset: int = 10
    columns: int = 6
    polaroid: bool = False
    shadow: bool = True
    auto_orient: bool = True

    def build(
        self,
        images: Iterable[Path],
        output: Path,
        filenames: bool = False,
        title: Optional[str] = None,
    ) -> str:
        command = [
            TOOLS.montage,
            "-geometry",
            f"{self.th_size}^+{self.th_offset}+{self.th_offset}",
            "-tile",
            self.columns,
        ]
        if title is not None:
            command += ["-title", title]
        if filenames:
            command += ["-label", r"%f"]
        if self.background:
            command += ["-background", self.background]
        if self.auto_orient:
            command.append("-auto-orient")
        if self.polaroid:
            command.append("+polaroid")
        if self.shadow:
            command += ["-shadow"]
        command += images
        command.append(output)
        assert not output.exists()
        command = list(map(str, command))
        check_call(command)
        return shlex.join(command)
