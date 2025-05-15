import subprocess
import sys

from B07nxs2txt import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "B07nxs2txt", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
