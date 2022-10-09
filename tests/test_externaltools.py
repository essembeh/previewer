from pathlib import Path

from previewer.external import *


def test_echo():

    echo = ExternalTool("echo")

    with echo.new_command("Hello World") as cmd:
        cmd.append("an argument")
        cmd += ["another"]
        cmd.append_if(True, Path("/foo"))
        cmd.append_if(False, Path("/bar"))
        check_call(cmd.command)
        assert str(cmd) == "echo 'Hello World' 'an argument' another /foo"
