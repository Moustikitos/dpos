# -*- coding: utf-8 -*-
# © Toons

import os
import unittest
import dposlib

from dposlib import rest


class TestDposApi(unittest.TestCase):

	@classmethod
	def setUpClass(self):
		# initialize on ark devnet
		rest.use("dark")
		# secrets used for testing
		self.secret = "secret"
		self.secondSecret = "secondSecret"
		self.wallet = dposlib.core.api.Wallet(
			dposlib.core.crypto.getAddress(dposlib.core.crypto.getKeys(self.secret)["publicKey"])
		)

	def test_networks(self):
		path = os.path.join(dposlib.ROOT, "network")
		for name in [n.replace(".net", "") for n in os.listdir(path) if n.endswith(".net")]:
			try:
				self.assertEqual(rest.use(name), True)
			except Exception as e:
				raise e
		rest.use("dark")

	def test_wallet(self):
		dgt = dposlib.core.api.Wallet(self.wallet.username)
		self.assertEqual(dgt.address, self.wallet.address)

	def test_wallet_link(self):
		self.wallet.link(self.secret, self.secondSecret)
		self.assertEqual(dposlib.blockchain.Transaction._publicKey, self.wallet.publicKey)
		self.assertEqual(dposlib.blockchain.Transaction._secondPublicKey, self.wallet.secondPublicKey)
