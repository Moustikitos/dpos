# -*- coding: utf-8 -*-

"""
`dposlib.cfg` module is used to store global blockchain parameters.

*Hard coded on import:*

name     |description
---------|-----------
headers  |headers used on each HTTP request
timeout  |HTTP request timeout response
peers    |list of blockchain peer to be used
txversion|global transaction version
"""

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Python/dposlib"
}

timeout = 5
peers = []
txversion = 1
