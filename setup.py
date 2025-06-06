#!/usr/bin/env python

import importlib
import os
import subprocess
from textwrap import dedent
from types import SimpleNamespace

from setuptools import Command, find_packages, setup

PACKAGE = "varscan_tool"

INSTALL_REQUIRES = []

DEV_REQUIRES = [
    "detect-secrets==0.13.1",
    "flake8",
    "isort",
    "mock",
    "pre-commit",
    "pytest",
    "pytest-cov",
]


GIT_COMMANDS = SimpleNamespace(
    branch=["git", "rev-parse", "--abbrev-ref", "HEAD"],
    commit=["git", "rev-list", "--count", "HEAD"],
    hash=["git", "rev-parse", "HEAD"],
    shorthash=["git", "rev-parse", "--short", "HEAD"],
)


VERSION_FILE_STR = dedent(
    """
    #!/usr/bin/env python
    # Auto-generated via setup.py
    __short_version__ = "{__short_version__}"
    __long_version__ = "{__long_version__}"
    __pypi_version__ = "{__pypi_version__}"

    if __name__ == "__main__":
        import sys

        argv = ' '.join(sys.argv)
        if 'short' in argv:
            print(__short_version__)
        elif 'pypi' in argv:
            print(__pypi_version__)
        else:
            print(__long_version__)
    """
).lstrip()


def write_version_file(**kwargs):
    file_path = os.path.join(PACKAGE, "_version.py")
    with open(file_path, "w") as fh:
        fh.write(VERSION_FILE_STR.format(**kwargs))


try:
    # Set versions if version file exists
    mod = importlib.import_module("{}._version".format(PACKAGE))
    __pypi_version__ = mod.__pypi_version__
    __long_version__ = mod.__long_version__
    __short_version__ = mod.__short_version__
except Exception:
    # Set defaults otherwise
    __pypi_version__ = "0.0.0"
    __long_version__ = "0.0.0"
    __short_version__ = "0.0.0"
    write_version_file(
        __pypi_version__=__pypi_version__,
        __long_version__=__long_version__,
        __short_version__=__short_version__,
    )


class PrintVersion(Command):
    description = "Print out specified version, default long version."
    user_options = [
        ("pypi", None, "Print package version."),
        ("short", None, "Print semantic version."),
        ("hash", None, "Print commit hash."),
    ]

    def initialize_options(self):
        self.pypi = False
        self.short = False
        self.hash = False

    def finalize_options(self):
        pass

    def run(self):
        if self.pypi:
            print(__pypi_version__)
        elif self.short:
            print(__short_version__)
        elif self.hash:
            try:
                commit_hash = call_subprocess(GIT_COMMANDS.hash)
            except Exception:
                print("")
            else:
                print(commit_hash)
        else:
            print(__long_version__)


class CaptureVersion(Command):
    """Writes version strings to MODULE/_version.py.

    Example:
        python setup.py -q capture_version --semver 1.2.3 --branch release/1.2.3
    """

    description = "Write version strings to _version.py."
    user_options = [
        ("semver=", None, "Semantic version."),
        ("branch=", None, "Git branch name."),
    ]

    def initialize_options(self):
        self.semver = None
        self.branch = None

    def finalize_options(self):
        assert self.semver is not None, "Provide semver"

        if self.branch is None or self.branch == "unknown":
            try:
                self.branch = call_subprocess(GIT_COMMANDS.branch)
            except Exception:
                self.branch = None

    def run(self):
        branch_name = self.branch or "unknown"

        git_short_hash = call_subprocess(GIT_COMMANDS.shorthash)
        git_commit = call_subprocess(GIT_COMMANDS.commit)

        __long_version__ = f"{self.semver}-{git_commit}.{git_short_hash}"
        __pypi_version__ = self.get_pypi_version(git_commit, branch_name)

        write_version_file(
            __pypi_version__=__pypi_version__,
            __long_version__=__long_version__,
            __short_version__=self.semver,
        )
        print(__long_version__)

    def get_pypi_version(self, commit, branch):
        fmt_str = "{semver}{suffix}"
        suffix = get_pypi_suffix(branch, commit)
        return fmt_str.format(semver=self.semver, suffix=suffix)


def call_subprocess(cmd: list):
    """Return stdout of given command."""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    stdout, _ = p.communicate()
    return stdout.decode().strip()


def get_pypi_suffix(branch, commit) -> str:
    """Return PEP 440-compatible suffix based on branch type."""
    if branch == "master":
        return ""
    elif branch.startswith("hotfix"):
        return ".post{}".format(commit)
    elif branch.startswith("feat"):
        return ".dev{}".format(commit)
    elif branch.startswith("release"):
        return ".rc{}".format(commit)
    else:
        return "a{}".format(commit)


class Requirements(Command):
    description = "foobar"
    user_options = [
        ("dev", None, "Bundles all requirements"),
    ]

    def initialize_options(self):
        self.dev = False

    def finalize_options(self):
        pass

    def run(self):
        if self.dev:
            path = os.path.join(".", "requirements.in")
            self.write_requirements(path, INSTALL_REQUIRES + DEV_REQUIRES)
        return

    def write_requirements(self, path, reqs):
        with open(path, "w") as fh:
            fh.write("\n".join(reqs) + "\n")


setup(
    name=PACKAGE,
    description="Varscan utilities.",
    version=__pypi_version__,
    python_requires=">=3.7",
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    tests_require=DEV_REQUIRES,
    cmdclass={
        "capture_requirements": Requirements,
        "capture_version": CaptureVersion,
        "print_version": PrintVersion,
    },
    scripts=[os.path.join(os.path.dirname(__file__), "bin", PACKAGE)],
)

# __END__
