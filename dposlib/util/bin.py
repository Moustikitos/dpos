# -*- coding: utf-8 -*-

import re
import struct
import binascii
import base58

# from dposlib import PY3

HEX = re.compile("^[0-9a-fA-F]*$")
BHEX = re.compile(b"^[0-9a-fA-F]*$")


def intasb(i):
    # int as byte conversion
    return unhexlify("%x" % i)


def basint(e):
    # byte as int conversion
    return struct.unpack("B", e)[0]


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
    return pack("<%ss" % len(v), f, (v,))


def hexlify(data):
    if isinstance(data, str):
        if HEX.match(data):
            return data
        else:
            data = data.encode()
    result = binascii.hexlify(data)
    return str(result.decode() if isinstance(result, bytes) else result)


def unhexlify(data):
    if isinstance(data, bytes):
        if BHEX.match(data):
            data = data.decode()
        else:
            raise Exception("Non hexadecimal digit found")
    if len(data) % 2:
        data = "0" + data
    result = binascii.unhexlify(data)
    return result if isinstance(result, bytes) else result.encode()


def checkAddress(address, awaited_marker=None):
    decoded = base58.b58decode_check(address)
    if decoded:
        if awaited_marker is not None:
            assert decoded[0] == awaited_marker, "wrong network address"
        return address
