#!/usr/bin/env python3
import shlex
import subprocess
from types import SimpleNamespace
from typing import IO, List, NamedTuple, Optional

DI = SimpleNamespace(subprocess=subprocess)


class PopenReturn(NamedTuple):
    retcode: int
    stdout: Optional[str]
    stderr: Optional[str]


def call_subprocess(
    cmd, timeout: Optional[int] = None, _di=DI, **kwargs
) -> PopenReturn:
    """Run subprocess command.
    Accepts:
        cmd (str): Command to run
        timeout (Optional[int]): Max time to wait, seconds
        kwargs: Extra args for Popen
    Raises:
        ValueError: Invalid kwargs
    Returns:
        PopenReturn: Stdout, stderr, and retcode of run command
    """

    if kwargs.get("shell", False):
        p = _di.subprocess.Popen(cmd, **kwargs)
    else:
        p = _di.subprocess.Popen(shlex.split(cmd), **kwargs)
    try:
        stdout, stderr = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        stdout, stderr = p.communicate()

    try:
        stdout = stdout.decode()
    except AttributeError:
        pass

    try:
        stderr = stderr.decode()
    except AttributeError:
        pass

    return PopenReturn(retcode=p.returncode, stdout=stdout, stderr=stderr)


def merge_outputs(files: List[str], output_file: IO):
    """Merge scattered outputs"""
    first = True
    for f in files:
        with open(f) as fh:
            for line in fh:
                if first or not line.startswith("#"):
                    output_file.write(line)
        first = False
    return


# __END__
