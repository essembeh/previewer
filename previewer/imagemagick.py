from dataclasses import dataclass
from pathlib import Path
from subprocess import check_call
from typing import Iterable, Optional

from .external import MONTAGE
from .logger import DEBUG
from .resolution import Resolution
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

        with MONTAGE.new_command() as cmd:
            images = list(images)
            cmd += [
                "-tile",
                self.columns if len(images) > self.columns else len(images),
            ]
            if self.th_size is None:
                cmd += [
                    "-geometry",
                    f"+{self.th_offset}+{self.th_offset}",
                ]
            else:
                cmd += [
                    "-geometry",
                    f"{self.th_size}^+{self.th_offset}+{self.th_offset}",
                ]

            cmd.append_if(title is not None, "-title", title)
            # doc: https://imagemagick.org/script/escape.php
            cmd.append_if(filenames, "-label", r"%t")
            cmd.append_if(self.background, "-background", self.background)
            cmd.append_if(self.auto_orient, "-auto-orient")
            cmd.append_if(self.polaroid, "+polaroid")
            cmd.append_if(self.shadow, "-shadow")
            cmd.append_if(self.font is not None, "-font", self.font)
            cmd += images
            cmd.append(output_jpg)

            DEBUG("montage command: %s", cmd)
            assert not output_jpg.exists()
            output_jpg.parent.mkdir(parents=True, exist_ok=True)
            cmd.check_call()
            check_image(output_jpg)
            return str(cmd)
