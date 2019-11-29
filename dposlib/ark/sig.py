# -*- encoding:utf-8 -*-

"""
Advanced signature manipulation. It is the recomended module to manually issue
signatures for ark blockchain and forks.

Variables:
  - ``privateKey`` (:class:`str`): hexlified private key
  - ``publicKey`` (:class:`str`):  hexlified compressed - encoded public key
  - ``message`` (:class:`str`):    message to sign as string
"""

from dposlib.ark import secp256k1
from dposlib.ark.secp256k1 import ecdsa, schnorr
from dposlib.util.bin import unhexlify


class Signature(list):
    r = property(
        lambda cls: list.__getitem__(cls, 0),
        None, None, "Signature part #1"
    )

    s = property(
        lambda cls: list.__getitem__(cls, 1),
        None, None, "Signature part #2"
    )

    der = property(
        lambda cls: cls._der_getter(),
        lambda cls, v: setattr(cls, "_der", v),
        None, "Return DER encoded signature as bytes sequence"
    )

    raw = property(
        lambda cls: cls._raw_getter(),
        lambda cls, v: setattr(cls, "_raw", v),
        None, "Return RAW Encode signature as bytes sequence"
    )

    def __init__(self, *rs):
        list.__init__(self, [int(e) for e in rs])

    def __repr__(self):
        return "<secp256k1 signature:\n  r:%064x\n  s:%064x\n>" % tuple(self)

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
        """
        Check if public key match message signature according to ``ECDSA``
        scheme.

        Args:
            message (:class:`str`): message to verify
            publicKey (:class:`str`): public key
        Returns:
            :class:`bool`: True if match
        """
        return ecdsa.verify(
            secp256k1.hash_sha256(message),
            secp256k1.Point.decode(unhexlify(publicKey)).encode(),
            self.der
        )

    def b410_schnorr_verify(self, message, publicKey):
        """
        Check if public key match message signature according to
        `Bcrypto 4.10 schnorr <https://github.com/bcoin-org/bcrypto/blob/v4.1.\
0/lib/js/schnorr.js>`_ scheme.

        Args:
            message (:class:`str`): message to verify
            publicKey (:class:`str`): public key
        Returns:
            :class:`bool`: True if match
        """
        return schnorr.bcrypto410_verify(
            secp256k1.hash_sha256(message),
            secp256k1.Point.decode(unhexlify(publicKey)).encode(),
            self.raw
        )

    def schnorr_verify(self, message, publicKey):
        """
        Check if public key match message signature according to
        `BIP schnorr <https://github.com/sipa/bips/blob/bip-schnorr/bip-schnor\
r.mediawiki>`_ scheme.

        Args:
            message (:class:`str`): message to verify
            publicKey (:class:`str`): public key
        Returns:
            :class:`bool`: True if match
        """
        return schnorr.verify(
            secp256k1.hash_sha256(message),
            schnorr.bytes_from_point(
                secp256k1.Point.decode(unhexlify(publicKey))
            ),
            self.raw
        )

    @staticmethod
    def from_raw(raw):
        """
        Decode signature from RAW encoded bytes sequence.

        Arguments:
            raw (:class:`bytes`): encoded signature
        Returns:
            :class:`Signature`: signature
        """
        length = len(raw) // 2
        sig = Signature(
            secp256k1.int_from_bytes(raw[:length]),
            secp256k1.int_from_bytes(raw[length:]),
        )
        sig._raw = raw
        return sig

    @staticmethod
    def from_der(der):
        """
        Decode signature from DER encoded bytes sequence.

        Arguments:
            der (:class:`bytes`): encoded signature
        Returns:
            :class:`Signature`: signature
        """
        sig = Signature(*secp256k1.sig_from_der(der))
        sig._der = der
        return sig

    @staticmethod
    def ecdsa_sign(message, privateKey, canonical=True):
        """
        Generate message signature according to ``ECDSA`` scheme using a random
        nonce.

        Args:
            message (:class:`str`): message to verify
            privateKey (:class:`str`): private key
            canonical (:class:`bool`): canonalize signature
        Returns:
            :class:`Signature`: signature
        """
        return Signature.from_der(
            ecdsa.sign(
                secp256k1.hash_sha256(message), unhexlify(privateKey),
                canonical=canonical
            )
        )

    @staticmethod
    def ecdsa_rfc6979_sign(message, privateKey, canonical=True):
        """
        Generate message signature according to ``ECDSA`` scheme using a
        deterministic nonce (RFC-6976).

        Args:
            message (:class:`str`): message to verify
            privateKey (:class:`str`): private key
            canonical (:class:`bool`): canonalize signature
        Returns:
            :class:`Signature`: signature
        """
        return Signature.from_der(
            ecdsa.rfc6979_sign(
                secp256k1.hash_sha256(message), unhexlify(privateKey),
                canonical=canonical
            )
        )

    @staticmethod
    def b410_schnorr_sign(message, privateKey):
        """
        Generate message signature according to
        `Bcrypto 4.10 schnorr <https://github.com/bcoin-org/bcrypto/blob/v4.1.\
0/lib/js/schnorr.js>`_ scheme.

        Args:
            message (:class:`str`): message to verify
            privateKey (:class:`str`): private key
        Returns:
            :class:`Signature`: signature
        """
        return Signature.from_raw(
            schnorr.bcrypto410_sign(
                secp256k1.hash_sha256(message), unhexlify(privateKey)
            )
        )

    @staticmethod
    def schnorr_sign(message, privateKey):
        """
        Generate message signature according to
        `BIP schnorr <https://github.com/sipa/bips/blob/bip-schnorr/bip-schnor\
r.mediawiki>`_ scheme.

        Args:
            message (:class:`str`): message to verify
            privateKey (:class:`str`): private key
        Returns:
            :class:`Signature`: signature
        """
        return Signature.from_raw(
            schnorr.sign(
                secp256k1.hash_sha256(message), unhexlify(privateKey)
            )
        )
