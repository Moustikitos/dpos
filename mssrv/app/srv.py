#! /usr/bin/env python
# -*- encoding:utf-8 -*-

"""
Usage:
   srv [-h <host> -p <port> -m <peer> -d]

Options:
-d --debug          : debug mode  [default: False]
-p --port=<port>    : the port you want to use  [default: 5001]
-h --host=<host>    : the host ip you want to use  [default: 127.0.0.1]
-m --ms-peer=<peer> : multisignature server peer  [default: http://127.0.0.1:5000]
"""

import sys
import docopt

from mssrv.app import app, _ark_srv_synch, _storage_clean_up, _link_peer
from dposlib.util.asynch import setInterval

setInterval(60)(_ark_srv_synch)()
setInterval(60)(_storage_clean_up)()


def create_app(mssrv):
    _link_peer(mssrv)
    return app


if __name__ == "__main__":
    args = docopt.docopt(__doc__, argv=sys.argv[1:])
    create_app(args["--ms-peer"])
    app.config.update(DEBUG=args["--debug"])
    app.run(host=args["--host"], port=int(args["--port"]))
