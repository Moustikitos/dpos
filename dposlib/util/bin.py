# -*- coding: utf-8 -*-

"""
Binary data manipulation that perform samely on python 2.x and 3.x.
"""

import re
import struct
import binascii

from dposlib import PY3

HEX = re.compile("^[0-9a-fA-F]$")
BHEX = re.compile(b"^[0-9a-fA-F]$")


def intasb(i):
    # int as byte conversion
    return unhexlify("%x" % i)


def basint(e):
    # byte as int conversion
    if not PY3:
        e = ord(e)
    return e


def unpack(fmt, fileobj):
    # read value as binary data from buffer
    return struct.unpack(fmt, fileobj.read(struct.calcsize(fmt)))


def pack(fmt, fileobj, values):
    # write value as binary data into buffer
    return fileobj.write(struct.pack(fmt, *values))


def unpack_bytes(f, n):
    # read bytes from buffer
    return unpack("<%ss" % n, f)[0]


def pack_bytes(f, v):
    # write bytes into buffer
    output = pack("<%ss" % len(v), f, (v,))
    return output


def hexlify(data):
    if PY3 and isinstance(data, str):
        if HEX.match(data):
            return data
        else:
            data = data.encode()
    result = binascii.hexlify(data)
    return str(result.decode() if isinstance(result, bytes) else result)


def unhexlify(data):
    if PY3 and isinstance(data, bytes):
        if BHEX.match(data):
            data = data.decode()
        else:
            raise Exception("Non hexadecimal digit found")
    if len(data) % 2:
        data = "0" + data
    result = binascii.unhexlify(data)
    return result if isinstance(result, bytes) else result.encode()
