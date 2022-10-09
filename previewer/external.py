import shlex
from collections import UserList
from contextlib import contextmanager
from dataclasses import dataclass
from functools import cached_property
from os import environ
from subprocess import DEVNULL, check_call, check_output
from typing import Any, Generator, List, Optional


class ExternalToolCommand(UserList):
    @property
    def command(self) -> List[str]:
        return [str(x) for x in self]

    def __str__(self):
        return shlex.join(self.command)

    def append_if(self, test: Any, *args: Any):
        if test:
            self += args

    def check_call(self, **kwargs):
        return check_call(self.command, **kwargs)

    def check_output(self, **kwargs):
        return check_output(self.command, **kwargs)


@dataclass
class ExternalTool:
    """
    helper to run external tools
    """

    _binary: str
    env_var: Optional[str] = None
    version_arg: str = "--version"

    @cached_property
    def binary(self):
        """
        find and test that the binary is executable
        """
        out = environ.get(self.env_var, self._binary) if self.env_var else self._binary
        if self.version_arg is not None:
            check_call([out, self.version_arg], stdout=DEVNULL, stderr=DEVNULL)
        return out

    def cmd(self, arguments: List[Any]) -> List[str]:
        """
        build the command to execute given the prog arguments
        """
        return [self.binary] + [str(x) for x in arguments]

    @contextmanager
    def new_command(self, *args) -> Generator[ExternalToolCommand, None, None]:
        out = ExternalToolCommand([self.binary])
        out += args
        yield out


FF_PROBE = ExternalTool("ffprobe", env_var="FFPROBE_BIN", version_arg="-version")
FF_MPEG = ExternalTool("ffmpeg", env_var="FFMPEG_BIN", version_arg="-version")
MONTAGE = ExternalTool("montage", env_var="MONTAGE_BIN")
