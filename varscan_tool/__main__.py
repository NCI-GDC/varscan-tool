#!/usr/bin/env python3
import sys

from varscan_tool import multi_varscan

if __name__ == "__main__":
    # CLI Entrypoint.
    retcode = 0

    try:
        retcode = multi_varscan.main()

    except Exception as e:
        retcode = 1

    sys.exit(retcode)

# __END__
