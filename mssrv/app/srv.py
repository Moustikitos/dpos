#! /usr/bin/env python
# -*- encoding:utf-8 -*-

"""
Usage:
   srv [-h <host> -p <port> -m <peer>]

Options:
-p --port=<port>    : the port you want to use     [default: 5001]
-h --host=<host>    : the host ip you want to use  [default: 127.0.0.1]
-m --ms-peer=<peer> : multisignature server peer   [default: http://127.0.0.1:5000]
"""

import sys
import docopt


if __name__ == "__main__":
    from mssrv.app import app
    args = docopt.docopt(__doc__, argv=sys.argv[1:])
    app.peer = args["--ms-peer"]
    app.run(host=args["--host"], port=int(args["--port"]))
