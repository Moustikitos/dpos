# -*- encoding:utf-8 -*-

import re
import sys
import binasci

from . import ecdsa, schnorr


HEX = re.compile("^[0-9a-fA-F]$")
BHEX = re.compile(b"^[0-9a-fA-F]$")
PY3 = True if sys.version_info[0] >= 3 else False


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
            return data
    if len(data) % 2:
        data = "0" + data
    result = binascii.unhexlify(data)
    return result if isinstance(result, bytes) else result.encode()


class Signature(list):
    r = property(lambda cls: list.__getitem__(cls, 0), None, None, "")
    s = property(lambda cls: list.__getitem__(cls, 1), None, None, "")

    def __init__(self, *rs):
        list.__init__(self, [int(e) for e in rs])

    def raw(self):
        return bytes_from_int(self.r) + bytes_from_int(self.s)

    def der(self):
        return der_from_sig(*self)

    def ecdsa_sign(self, message, privateKey):
        return Signature.der_decode(
            ecdsa.sign(hash_sha256(message), unhexlify(privateKey))
        )

    def b410_schnorr_sign(self, message, privateKey):
        return Signature.raw_decode(
            schnorr.bcrypto410_sign(
                hash_sha256(message), unhexlify(privateKey)
            )
        )

    def schnorr_sign(self, message, privateKey):
        return Signature.raw_decode(
            schnorr.sign(hash_sha256(message), unhexlify(privateKey))
        )

    def ecdsa_verify(self, message, publicKey):
        return ecdsa.verify(
            hash_sha256(message),
            ecdsa.Point.decode(publicKey).encode(),
            self.der()
        )

    def b410_schnorr_verify(self, message, publicKey):
        return schnorr.bcrypto410_verify(
            hash_sha256(message),
            schnorr.Point.decode(publicKey).encode(),
            self.raw()
        )

    def schnorr_verify(self, message, publicKey):
        return schnorr.verify(
            hash_sha256(message),
            schnorr.encoded_from_point(schnorr.Point.decode(publicKey)),
            self.raw()
        )

    @staticmethod
    def raw_decode(raw):
        raw = unhexlify(raw)
        length = len(raw) // 2
        return Signature(
            int_from_bytes(raw[:length]),
            int_from_bytes(raw[length:]),
        )

    @staticmethod
    def der_decode(der):
        der = unhexlify(der)
        return Signature(*sig_from_der(der))
