from functools import cached_property
from os import getenv
from subprocess import DEVNULL, check_call
from typing import Optional


class _Tools:
    def __find_binary(
        self,
        name: str,
        env_variable: Optional[str] = None,
        arg_version: str = "--version",
    ) -> str:
        if env_variable is None:
            env_variable = f"{name.upper}_BIN"
        binary = getenv(env_variable, name)
        check_call([binary, arg_version], stdout=DEVNULL, stderr=DEVNULL)
        return binary

    @cached_property
    def ffprobe(self) -> str:
        return self.__find_binary("ffprobe", arg_version="-version")

    @cached_property
    def ffmpeg(self) -> str:
        return self.__find_binary("ffmpeg", arg_version="-version")

    @cached_property
    def montage(self) -> str:
        return self.__find_binary("montage")


TOOLS = _Tools()
