#! /usr/bin/env python
# -*- encoding:utf-8 -*-

"""
Usage:
   srv [-h <host>] [-p <port>]

Options:
-p --port=<port> : the port you want to use  [default: 5000]
-h --host=<host> : the host ip you want to use  [default: 0.0.0.0]
"""

import os
import sys
import docopt

from mssrv import app

# add parent path if executed from git structure
sys.path.append(
    os.path.normpath(
        os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )
    )
)

if __name__ == "__main__":
    args = docopt.docopt(__doc__, argv=sys.argv[1:])
    app.run(host=args["--host"], port=int(args["--port"]))
