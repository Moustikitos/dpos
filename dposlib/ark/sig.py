# -*- encoding:utf-8 -*-

"""
Advanced signature manipulation. It is the recomended module to manually issue
signatures for ark blockchain and forks.

Variables:
  - ``privateKey`` (:class:`str`): hexlified private key
  - ``publicKey`` (:class:`str`):  hexlified compressed - encoded public key
  - ``message`` (:class:`str`):    message to sign as string
"""

import secp256k1

from secp256k1 import ecdsa, schnorr
from dposlib.util.bin import hexlify, unhexlify


class Signature(list):
    r = property(
        lambda cls: list.__getitem__(cls, 0),
        None, None, ""
    )

    s = property(
        lambda cls: list.__getitem__(cls, 1),
        None, None, ""
    )

    der = property(
        lambda cls: cls._der_getter(),
        lambda cls, v: setattr(cls, "_der", v),
        None, ""
    )

    raw = property(
        lambda cls: cls._raw_getter(),
        lambda cls, v: setattr(cls, "_raw", v),
        None, ""
    )

    def __init__(self, *rs):
        list.__init__(self, [int(e) for e in rs])

    def _der_getter(cls):
        if not hasattr(cls, "_der"):
            setattr(cls, "_der", secp256k1.der_from_sig(*cls))
        return getattr(cls, "_der")

    def _raw_getter(cls):
        if not hasattr(cls, "_raw"):
            setattr(
                cls, "_raw",
                secp256k1.bytes_from_int(cls[0]) +
                secp256k1.bytes_from_int(cls[1])
            )
        return getattr(cls, "_raw")

    def ecdsa_verify(self, message, publicKey):
        return ecdsa.verify(
            secp256k1.hash_sha256(message),
            secp256k1.Point.decode(unhexlify(publicKey)).encode(),
            self.der()
        )

    def b410_schnorr_verify(self, message, publicKey):
        return schnorr.bcrypto410_verify(
            secp256k1.hash_sha256(message),
            secp256k1.Point.decode(unhexlify(publicKey)).encode(),
            self.raw()
        )

    def schnorr_verify(self, message, publicKey):
        return schnorr.verify(
            secp256k1.hash_sha256(message),
            schnorr.bytes_from_point(
                secp256k1.Point.decode(unhexlify(publicKey))
            ),
            self.raw()
        )

    @staticmethod
    def from_raw(raw):
        # raw = unhexlify(raw)
        length = len(raw) // 2
        sig = Signature(
            secp256k1.int_from_bytes(raw[:length]),
            secp256k1.int_from_bytes(raw[length:]),
        )
        sig._raw = raw
        return sig

    @staticmethod
    def from_der(der):
        # der = unhexlify(der)
        sig = Signature(*secp256k1.sig_from_der(der))
        sig._der = der
        return sig

    @staticmethod
    def ecdsa_sign(message, privateKey, canonical=True):
        return Signature.from_der(
            ecdsa.sign(
                secp256k1.hash_sha256(message), unhexlify(privateKey),
                canonical=canonical
            )
        )

    @staticmethod
    def ecdsa_rfc6979_sign(message, privateKey, canonical=True):
        return Signature.from_der(
            ecdsa.rfc6979_sign(
                secp256k1.hash_sha256(message), unhexlify(privateKey),
                canonical=canonical
            )
        )

    @staticmethod
    def b410_schnorr_sign(message, privateKey):
        return Signature.from_raw(
            schnorr.bcrypto410_sign(
                secp256k1.hash_sha256(message), unhexlify(privateKey)
            )
        )

    @staticmethod
    def schnorr_sign(message, privateKey):
        return Signature.from_raw(
            schnorr.sign(
                secp256k1.hash_sha256(message), unhexlify(privateKey)
            )
        )
