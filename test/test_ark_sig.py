# -*- coding: utf-8 -*-
# © Toons

import unittest

from dposlib import rest
from dposlib.ark.sig import Signature, hexlify, unhexlify
from dposlib.ark import secp256k1


class TestArkSig(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        prikey0 = secp256k1.hash_sha256("secret")
        self.publicKey = hexlify(
            secp256k1.PublicKey.from_seed(prikey0).encode()
        )
        self.privateKey = hexlify(prikey0)
        self.msg_der = "00993c0b0003a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1b"\
                       "b3f3a44c4a05e79f19de9331eb8dd0e799b69714269474be623ce"\
                       "b3309020dff5756e69746573743a20747820776974682073696d7"\
                       "06c65207369676e61747572650000000000000000000000000000"\
                       "000000000000000000000000000000000000e1f50500000000c04"\
                       "b030000000000"
        self.msg_raw = "ff0217010000000000010000000000000003a02b9d5fdd1307c2e"\
                       "e4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de933809698"\
                       "000000000000a08601000000000000000000171dfc69b54c7fe90"\
                       "1e91d5a9ab78388645e2427ea"
        self.der = "304402200ee92c78a690844eaabf6833ed4fe9c66db1476bcfaad1754"\
                   "aec780116aa16b0022045e8fda963191c1df485ff18966df509679d8d"\
                   "dd47e6fd51f2645309227fc5c9"
        self.raw = "4f01bd21828a633a3c821b9984fe642deab87237b99e62a543ca6948f"\
                   "f1d6d32f2475ada1f933da0591c40603693614afa69fcb4caa2b4be01"\
                   "8788de9f10c42a"

    def testSignatureDerPorperty(self):
        sig = Signature.from_der(unhexlify(self.der))
        self.assertEqual(
            True,
            sig.ecdsa_verify(
                unhexlify(self.msg_der),
                self.publicKey
            )
        )

    def testSignatureRawPorperty(self):
        sig = Signature.from_raw(unhexlify(self.raw))
        self.assertEqual(
            True,
            sig.b410_schnorr_verify(
                unhexlify(self.msg_raw),
                self.publicKey
            )
        )

    def testEcdsa(self):
        message = "simple message"
        sig = Signature.ecdsa_sign(
            message, self.privateKey,
            canonical=False
        )
        self.assertEqual(
            True,
            sig.ecdsa_verify(message, self.publicKey)
        )

    def testEcdsaCanonical(self):
        message = "simple message"
        sig = Signature.ecdsa_sign(
            message, self.privateKey,
            canonical=True
        )
        self.assertEqual(
            True,
            sig.ecdsa_verify(message, self.publicKey)
        )

    def testSchnorr(self):
        message = "simple message"
        sig = Signature.schnorr_sign(
            message, self.privateKey
        )
        self.assertEqual(
            True,
            sig.schnorr_verify(message, self.publicKey)
        )

    def testBcrypto410Schnorr(self):
        message = "simple message"
        sig = Signature.b410_schnorr_sign(
            message, self.privateKey
        )
        self.assertEqual(
            True,
            sig.b410_schnorr_verify(message, self.publicKey)
        )
