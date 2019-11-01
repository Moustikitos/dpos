# -*- coding: utf-8 -*-
# © Toons

import unittest
import dposlib
import json
import os

from dposlib import rest
from dposlib import blockchain
from dposlib.util import bin as bin_
from dposlib.util import data


class TestArkCryptoV2(unittest.TestCase):

	@classmethod
	def setUpClass(self):
		def fix_fixture(tx):
			for key in [k for k in ["amount", "fee", "nonce"] if k in tx]:
				tx[key] = int(tx.pop(key))
			return tx

		self.fixtures = [fix_fixture(tx) for tx in data.loadJson(os.path.join(
			os.path.abspath(os.path.dirname(__file__)),
			"fixtures.json"
		))]
		rest.use("ark")

	def test_serialization(self):
		for tx in self.fixtures[:]:
			serialized = tx.pop("serialized", False)
			id_ = tx.pop("id", False)
			sig = tx.pop("signature", False)
			sigs = tx.pop("signatures", False)
			t = blockchain.Transaction(tx)
			t.signature = sig
			if sigs:
				signatures = [None] * (max(int(s[:2], 16) for s in sigs)+1)
				for elem in sigs:
					print(int(elem[:2], 16), elem[2:])
					signatures[int(elem[:2], 16)] = elem[2:] 
				t.signatures = signatures
			
			computed = bin_.hexlify(dposlib.core.crypto.getBytes(t, exclude_multi_sig=not t['type'] == 4))
			# print(serialized)
			# print(computed)
			# print(serialized == computed)
			self.assertEqual(serialized, computed)
			self.assertEqual(id_, dposlib.core.crypto.getId(t))
