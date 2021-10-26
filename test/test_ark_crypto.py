# -*- coding: utf-8 -*-

import unittest
import dposlib

from dposlib import rest
from dposlib.util import bin as bin_


class TestArkCrypto(unittest.TestCase):

    tx0_dict = {
        "amount": 100000000,
        "asset": {},
        "fee": 216000,
        "recipientId": "DMzZgqGrZkmyPGgUTULSw1XWPrbj9dVwM3",
        "senderPublicKey": "03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44"
                           "c4a05e79f19de933",
        "timestamp": 736409,
        "type": 0,
        "vendorField": "unitest: tx with simple signature"
    }

    signed_tx0_dict = {
        "amount": 100000000,
        "asset": {},
        "fee": 216000,
        "recipientId": "DMzZgqGrZkmyPGgUTULSw1XWPrbj9dVwM3",
        "senderId": "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk",
        "senderPublicKey": "03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44"
                           "c4a05e79f19de933",
        "signature": "304402200ee92c78a690844eaabf6833ed4fe9c66db1476bcfaad175"
                     "4aec780116aa16b0022045e8fda963191c1df485ff18966df509679d"
                     "8ddd47e6fd51f2645309227fc5c9",
        "timestamp": 736409,
        "type": 0,
        "vendorField": "unitest: tx with simple signature"
    }

    signSigned_tx0_dict = {
        "amount": 100000000,
        "asset": {},
        "fee": 216000,
        "recipientId": "DMzZgqGrZkmyPGgUTULSw1XWPrbj9dVwM3",
        "senderId": "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk",
        "senderPublicKey": "03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44"
                           "c4a05e79f19de933",
        "signSignature": "30440220387162239898ddf2abbbf5147c731c04ad7ea6dd3f01"
                         "9c1f1697f23b2d94873202200a224d7d5e80829eaa6bb269ab73"
                         "eec74f90b3dd987b5d485d93284878ab3ea5",
        "signature": "304402200ee92c78a690844eaabf6833ed4fe9c66db1476bcfaad175"
                     "4aec780116aa16b0022045e8fda963191c1df485ff18966df509679d"
                     "8ddd47e6fd51f2645309227fc5c9",
        "timestamp": 736409,
        "type": 0,
        "vendorField": "unitest: tx with simple signature"
    }

    signed_tx0_hex = \
        "00993c0b0003a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79"\
        "f19de9331eb8dd0e799b69714269474be623ceb3309020dff5756e69746573743a20"\
        "747820776974682073696d706c65207369676e617475726500000000000000000000"\
        "00000000000000000000000000000000000000000000e1f50500000000c04b030000"\
        "000000304402200ee92c78a690844eaabf6833ed4fe9c66db1476bcfaad1754aec78"\
        "0116aa16b0022045e8fda963191c1df485ff18966df509679d8ddd47e6fd51f26453"\
        "09227fc5c9"

    signSigned_tx0_hex = \
        "00993c0b0003a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79"\
        "f19de9331eb8dd0e799b69714269474be623ceb3309020dff5756e69746573743a20"\
        "747820776974682073696d706c65207369676e617475726500000000000000000000"\
        "00000000000000000000000000000000000000000000e1f50500000000c04b030000"\
        "000000304402200ee92c78a690844eaabf6833ed4fe9c66db1476bcfaad1754aec78"\
        "0116aa16b0022045e8fda963191c1df485ff18966df509679d8ddd47e6fd51f26453"\
        "09227fc5c930440220387162239898ddf2abbbf5147c731c04ad7ea6dd3f019c1f16"\
        "97f23b2d94873202200a224d7d5e80829eaa6bb269ab73eec74f90b3dd987b5d485d"\
        "93284878ab3ea5"

    @classmethod
    def setUpClass(self):
        # secrets used for testing
        self.secret = "secret"
        self.secondSecret = "secondSecret"
        # initialize on ark devnet
        rest.use("dark")

    def test_get_address(self):
        self.assertEqual(
            "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk",
            dposlib.core.crypto.getAddress(
                dposlib.core.crypto.getKeys(self.secret)["publicKey"]
            )
        )

    def test_get_keys(self):
        i = 0x2bb80d537b1da3e38bd30361aa855686bde0eacd7162fef6a25fe97bf527a25b
        s = "%x" % i
        b = b"%x" % i
        keys = dposlib.core.crypto.getKeys("secret")
        self.assertEqual(keys, dposlib.core.crypto.getKeys(u"secret"))
        self.assertEqual(keys, dposlib.core.crypto.getKeys(b"secret"))
        self.assertEqual(keys, dposlib.core.crypto.getKeys(i))
        self.assertEqual(keys, dposlib.core.crypto.getKeys(s))
        self.assertEqual(keys, dposlib.core.crypto.getKeys(b))

    def test_schnorr_signature(self):
        keys = dposlib.core.crypto.getKeys(self.secret)
        message = b'\xff' + "test message".encode("utf-8")
        signature = dposlib.core.crypto.getSignatureFromBytes(
            message, keys["privateKey"]
        )
        self.assertEqual(
            True,
            dposlib.core.crypto.verifySignatureFromBytes(
                message, keys["publicKey"], signature
            )
        )

    def test_get_id(self):
        self.assertEqual(
            "0091128b8cb24758c8d1ed1dfe9c7ac3713691f54b96ce12ca3cbc675aa13d9a",
            dposlib.core.crypto.getId(TestArkCrypto.signed_tx0_dict)
        ) and self.assertEqual(
            "d6f5208aaf8988b97e12260c554d04a149845f0160aa82d8c53eaa0836d3cf56",
            dposlib.core.crypto.getId(TestArkCrypto.signSigned_tx0_dict)
        )

    def test_get_id_from_bytes(self):
        self.assertEqual(
            "0091128b8cb24758c8d1ed1dfe9c7ac3713691f54b96ce12ca3cbc675aa13d9a",
            dposlib.core.crypto.getIdFromBytes(
                bin_.unhexlify(TestArkCrypto.signed_tx0_hex)
            )
        ) and self.assertEqual(
            "d6f5208aaf8988b97e12260c554d04a149845f0160aa82d8c53eaa0836d3cf56",
            dposlib.core.crypto.getIdFromBytes(
                bin_.unhexlify(TestArkCrypto.signSigned_tx0_hex)
            )
        )

    def test_get_bytes_and_hexlify(self):
        self.assertEqual(
            TestArkCrypto.signed_tx0_hex,
            bin_.hexlify(dposlib.core.crypto.getBytes(
                TestArkCrypto.signed_tx0_dict)
            )
        )
        self.assertEqual(
            TestArkCrypto.signSigned_tx0_hex,
            bin_.hexlify(dposlib.core.crypto.getBytes(
                TestArkCrypto.signSigned_tx0_dict)
            )
        )

    def test_transaction_sign(self):
        tx = dposlib.core.Transaction(TestArkCrypto.tx0_dict)
        tx.link(self.secret, self.secondSecret)
        tx.sign()
        if tx.get("version", 1) >= 2:
            return None
        self.assertEqual(tx["signature"],
                         TestArkCrypto.signed_tx0_dict["signature"])
        self.assertEqual(bin_.hexlify(dposlib.core.crypto.getBytes(tx)),
                         TestArkCrypto.signed_tx0_hex)
        tx.signSign()
        self.assertEqual(tx["signSignature"],
                         TestArkCrypto.signSigned_tx0_dict["signSignature"])
        self.assertEqual(bin_.hexlify(dposlib.core.crypto.getBytes(tx)),
                         TestArkCrypto.signSigned_tx0_hex)
        tx.unlink()

    def test_wif_sign(self):
        keys = dposlib.core.crypto.getKeys(self.secret)
        tx = dposlib.core.Transaction(TestArkCrypto.tx0_dict)
        if tx.get("version", 1) >= 2:
            return None
        self.assertEqual(
            dposlib.core.crypto.wifSignature(tx, keys["wif"]),
            TestArkCrypto.signed_tx0_dict["signature"]
        )

    # def test_transaction_check(self):
    #     keys = dposlib.core.crypto.getKeys(self.secondSecret)
    #     self.assertEqual(dposlib.core.crypto.checkTransaction(
    #         TestArkCrypto.signed_tx0_dict
    #     ), True)
    #     self.assertEqual(dposlib.core.crypto.checkTransaction(
    #         TestArkCrypto.signSigned_tx0_dict, keys["publicKey"]
    #     ), True)
