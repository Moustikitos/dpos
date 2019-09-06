# -*- coding: utf-8 -*-
# © Toons

import unittest
import dposlib

from dposlib import rest
from dposlib.util import bin as bin_


class TestEcdsaCrypto(unittest.TestCase):

	tx0_dict = {
		"amount": 100000000,
		"asset": {},
		"fee": 216000,
		"recipientId": "DMzZgqGrZkmyPGgUTULSw1XWPrbj9dVwM3",
		"senderPublicKey":
			"03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de933",
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
		"senderPublicKey":
			"03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de933",
		"signature":
			"304402200ee92c78a690844eaabf6833ed4fe9c66db1476bcfaad1754aec780116"\
			"aa16b0022045e8fda963191c1df485ff18966df509679d8ddd47e6fd51f2645309"\
			"227fc5c9",
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
		"senderPublicKey":
			"03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de933",
		"signSignature":
			"30440220387162239898ddf2abbbf5147c731c04ad7ea6dd3f019c1f1697f23b2d"\
			"94873202200a224d7d5e80829eaa6bb269ab73eec74f90b3dd987b5d485d932848"\
			"78ab3ea5",
		"signature":
			"304402200ee92c78a690844eaabf6833ed4fe9c66db1476bcfaad1754aec780116"\
			"aa16b0022045e8fda963191c1df485ff18966df509679d8ddd47e6fd51f2645309"\
			"227fc5c9",
		"timestamp": 736409,
		"type": 0,
		"vendorField": "unitest: tx with simple signature"
	}

	signed_tx0_hex = \
		"00993c0b0003a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f1"\
		"9de9331eb8dd0e799b69714269474be623ceb3309020dff5756e69746573743a207478"\
		"20776974682073696d706c65207369676e617475726500000000000000000000000000"\
		"00000000000000000000000000000000000000e1f50500000000c04b03000000000030"\
		"4402200ee92c78a690844eaabf6833ed4fe9c66db1476bcfaad1754aec780116aa16b0"\
		"022045e8fda963191c1df485ff18966df509679d8ddd47e6fd51f2645309227fc5c9"

	signSigned_tx0_hex = \
		"00993c0b0003a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f1"\
		"9de9331eb8dd0e799b69714269474be623ceb3309020dff5756e69746573743a207478"\
		"20776974682073696d706c65207369676e617475726500000000000000000000000000"\
		"00000000000000000000000000000000000000e1f50500000000c04b03000000000030"\
		"4402200ee92c78a690844eaabf6833ed4fe9c66db1476bcfaad1754aec780116aa16b0"\
		"022045e8fda963191c1df485ff18966df509679d8ddd47e6fd51f2645309227fc5c930"\
		"440220387162239898ddf2abbbf5147c731c04ad7ea6dd3f019c1f1697f23b2d948732"\
		"02200a224d7d5e80829eaa6bb269ab73eec74f90b3dd987b5d485d93284878ab3ea5"
	
	def createTx0(self):
		# create a tx with fixed timestamp and dynamic fees values
		tx0 = dposlib.core.transfer(1, "DMzZgqGrZkmyPGgUTULSw1XWPrbj9dVwM3", vendorField="unitest: tx with simple signature")
		tx0.useDynamicFee(1000)
		tx0["timestamp"] = rest.cfg.begintime.toordinal()
		tx0.setFees()
		return tx0

	@classmethod
	def setUpClass(self):
		# secrets used for testing
		self.secret = "secret"
		self.secondSecret = "secondSecret"
		# initialize on ark devnet
		rest.use("d.ark")

	def test_get_address(self):
		self.assertEqual(
			"D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk",
			dposlib.core.crypto.getAddress(dposlib.core.crypto.getKeys(self.secret)["publicKey"])
		)

	def test_schnorr_signature(self):
		dposlib.core.crypto.SCHNORR_SIG = True
		keys = dposlib.core.crypto.getKeys(self.secret)
		message = "test message".encode("utf-8")
		signature = dposlib.core.crypto.getSignatureFromBytes(message, keys["privateKey"])
		self.assertEqual(
			True,
			dposlib.core.crypto.verifySignatureFromBytes(message, keys["publicKey"], signature)
		)
		dposlib.core.crypto.SCHNORR_SIG = False

	def test_get_id(self):
		self.assertEqual(
			"0091128b8cb24758c8d1ed1dfe9c7ac3713691f54b96ce12ca3cbc675aa13d9a",
			dposlib.core.crypto.getId(TestEcdsaCrypto.signed_tx0_dict)
		) and self.assertEqual(
			"d6f5208aaf8988b97e12260c554d04a149845f0160aa82d8c53eaa0836d3cf56",
			dposlib.core.crypto.getId(TestEcdsaCrypto.signSigned_tx0_dict)
		)

	def test_get_id_from_bytes(self):
		self.assertEqual(
			"0091128b8cb24758c8d1ed1dfe9c7ac3713691f54b96ce12ca3cbc675aa13d9a",
			dposlib.core.crypto.getIdFromBytes(bin_.unhexlify(TestEcdsaCrypto.signed_tx0_hex))
		) and self.assertEqual(
			"d6f5208aaf8988b97e12260c554d04a149845f0160aa82d8c53eaa0836d3cf56",
			dposlib.core.crypto.getIdFromBytes(bin_.unhexlify(TestEcdsaCrypto.signSigned_tx0_hex))
		)

	def test_get_bytes_and_hexlify(self):
		self.assertEqual(
			TestEcdsaCrypto.signed_tx0_hex,
			bin_.hexlify(dposlib.core.crypto.getBytes(TestEcdsaCrypto.signed_tx0_dict))
		)
		self.assertEqual(
			TestEcdsaCrypto.signSigned_tx0_hex,
			bin_.hexlify(dposlib.core.crypto.getBytes(TestEcdsaCrypto.signSigned_tx0_dict))
		)
	
	def test_transaction_link(self):
		dposlib.core.Transaction.link(self.secret, self.secondSecret)
		self.assertEqual(
			dposlib.core.crypto.verifySignatureFromBytes(
				dposlib.core.crypto.getBytes(TestEcdsaCrypto.tx0_dict),
				dposlib.core.Transaction._publicKey,
				TestEcdsaCrypto.signed_tx0_dict["signature"]
			),
			True
		)
		self.assertEqual(
			dposlib.core.crypto.verifySignatureFromBytes(
				dposlib.core.crypto.getBytes(TestEcdsaCrypto.signed_tx0_dict),
				dposlib.core.Transaction._secondPublicKey,
				TestEcdsaCrypto.signSigned_tx0_dict["signSignature"]
			),
			True
		)
		dposlib.core.Transaction.unlink()

	def test_transaction_sign(self):
		dposlib.core.crypto.SCHNORR_SIG = False
		dposlib.core.Transaction.link(self.secret, self.secondSecret)
		tx = dposlib.core.Transaction(TestEcdsaCrypto.tx0_dict)
		tx.sign()
		self.assertEqual(tx["signature"], TestEcdsaCrypto.signed_tx0_dict["signature"])
		self.assertEqual(bin_.hexlify(dposlib.core.crypto.getBytes(tx)), TestEcdsaCrypto.signed_tx0_hex)
		tx.signSign()
		self.assertEqual(tx["signSignature"], TestEcdsaCrypto.signSigned_tx0_dict["signSignature"])
		self.assertEqual(bin_.hexlify(dposlib.core.crypto.getBytes(tx)), TestEcdsaCrypto.signSigned_tx0_hex)
		dposlib.core.Transaction.unlink()

	def test_wif_sign(self):
		dposlib.core.crypto.SCHNORR_SIG = False
		keys = dposlib.core.crypto.getKeys(self.secret)
		tx = dposlib.core.Transaction(TestEcdsaCrypto.tx0_dict)
		self.assertEqual(dposlib.core.crypto.wifSignature(tx, keys["wif"]), TestEcdsaCrypto.signed_tx0_dict["signature"])

	def test_transaction_check(self):
		dposlib.core.crypto.SCHNORR_SIG = False
		keys = dposlib.core.crypto.getKeys(self.secondSecret)
		self.assertEqual(dposlib.core.crypto.checkTransaction(TestEcdsaCrypto.signed_tx0_dict), True)
		self.assertEqual(dposlib.core.crypto.checkTransaction(TestEcdsaCrypto.signSigned_tx0_dict, keys["publicKey"]), True)
