#!/usr/bin/env python
"""
Python Project Template Entrypoint Script
"""

import datetime
import logging
import sys

import click

try:
    from varscan_tool import __version__
except Exception:
    __version__ = "0.0.0"

log = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s:%(lineno)s %(levelname)s | %(message)s",
)


def run() -> int:
    """Method for running script logic.

    Accepts:
        run_args (namespace): Collection of parsed arguments
    Returns:
        ret_code (int): Return code for sys.exit()
    """

    ret_val = 0

    start_time = datetime.datetime.now()

    log.info("Running process...")

    # Log runtime info
    end_time = datetime.datetime.now()
    run_time = end_time - start_time
    log.info("Run time: %d seconds", run_time.seconds)
    return ret_val


@click.command()
@click.version_option(version=__version__)
# Add new cli args, e.g.:
# @click.option("--foo")
# @click.option("--bar")
# def main(foo: str, bar: int):
def main() -> int:
    """Main Entrypoint."""
    exit_code = 0
    args = sys.argv

    log.info("Version: %s", __version__)
    log.info("Process called with %s", args)

    try:
        exit_code = run()
    except Exception as e:
        log.exception(e)
        exit_code = 1
    return exit_code


if __name__ == "__main__":
    """CLI Entrypoint"""

    status_code = 0
    try:
        status_code = main()
    except Exception as e:
        log.exception(e)
        sys.exit(1)
    sys.exit(status_code)


# __END__
