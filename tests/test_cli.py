import shlex
from typing import List, Tuple
from unittest import mock

import pytest
from previewer import __name__ as prog
from previewer import __version__ as version
from previewer import cli


def run(capsys, args: str) -> Tuple[int, List[str], List[str]]:
    with pytest.raises(SystemExit) as error:
        with mock.patch("sys.argv", [prog] + shlex.split(args)):
            cli.run()
    captured = capsys.readouterr()
    return (
        error.value.code,
        captured.out.splitlines(),
        captured.err.splitlines(),
    )  # pyright: reportGeneralTypeIssues=false


def assert_no_error(
    rc: int, out: List[str], err: List[str]
) -> Tuple[int, List[str], List[str]]:
    assert rc == 0
    assert len(out) > 0
    assert len(err) == 0
    return rc, out, err


def test_help(capsys):
    assert_no_error(*run(capsys, "--help"))
    assert_no_error(*run(capsys, "montage --help"))
    assert_no_error(*run(capsys, "sequence --help"))
    assert_no_error(*run(capsys, "resize --help"))
    assert_no_error(*run(capsys, "frames --help"))


def test_version(capsys):
    _rc, out, _err = assert_no_error(*run(capsys, "--version"))
    assert len(out) == 1
    assert version in out[0]


def test_error(capsys):
    rc, out, err = run(capsys, "foo bar")
    assert rc > 0
    assert len(out) == 0
    assert len(err) > 0
