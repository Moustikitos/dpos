# -*- coding: utf-8 -*-
# © Toons

import os
import io
import unittest
import binascii

import pySecp256k1 as secp256k1
from pySecp256k1 import schnorr, ecdsa


with io.open(
    os.path.join(os.path.dirname(__file__), "test_vectors.csv"), "r"
) as test_vectors:
    SCHNORR_TEST_VECTORS = test_vectors.read()


class TestArkSecp256k1V2(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.test_vectors = dict([int(e[0]), e[1:5]+[eval(e[5])]] for e in
            [
                line.split(";") for line in
                SCHNORR_TEST_VECTORS.split("\n")[1:-1]
            ]
        )

    def testSchnorrVectors_1_5(self):
        test_vectors = self.test_vectors.values()
        for test_vector in [test for test in test_vectors if test[-1]]:
            secret0, pubkey, msg, sig, result = [
                binascii.unhexlify(e) for e in
                test_vector[:-1]] + [test_vector[-1]
            ]
            if secret0 != b'':
                self.assertEqual(pubkey, schnorr.bytes_from_point(
                    secp256k1.G * secp256k1.int_from_bytes(secret0))
                )
                self.assertEqual(sig, schnorr.sign(msg, secret0))
            self.assertEqual(result, schnorr.verify(msg, pubkey, sig))

    def testBcrypto410Schnorr(self):
        msg = secp256k1.hash_sha256("message to sign".encode())
        pr_key = secp256k1.hash_sha256("secret".encode())
        pu_key = secp256k1.encoded_from_point(
            secp256k1.G * secp256k1.int_from_bytes(pr_key)
        )
        self.assertEqual(
            True,
            schnorr.bcrypto410_verify(
                msg, pu_key,
                schnorr.bcrypto410_sign(msg, pr_key)
            )
        )

    def testSecp256k1Ecdsa(self):
        msg = secp256k1.hash_sha256("message to sign".encode())
        pr_key = secp256k1.hash_sha256("secret".encode())
        pu_key = secp256k1.encoded_from_point(
            secp256k1.G * secp256k1.int_from_bytes(pr_key)
        )
        self.assertEqual(
            True,
            ecdsa.verify(msg, pu_key, ecdsa.sign(msg, pr_key))
        )
        self.assertEqual(
            True,
            ecdsa.verify(msg, pu_key, ecdsa.sign(msg, pr_key, canonical=False))
        )

    def testSecp256k1Rfc6979Ecdsa(self):
        msg = secp256k1.hash_sha256("message to sign".encode())
        pr_key = secp256k1.hash_sha256("secret".encode())
        pu_key = secp256k1.encoded_from_point(
            secp256k1.G * secp256k1.int_from_bytes(pr_key)
        )
        self.assertEqual(
            True,
            ecdsa.verify(msg, pu_key, ecdsa.rfc6979_sign(msg, pr_key))
        )
        self.assertEqual(
            True,
            ecdsa.verify(msg, pu_key, ecdsa.rfc6979_sign(
                msg, pr_key, canonical=False)
            )
        )
