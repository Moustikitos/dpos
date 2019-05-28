# -*- coding: utf-8 -*-
# © Toons

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

	def test_wallet(self):
		dgt = dposlib.core.api.Wallet(self.wallet.username)
		self.assertEqual(dgt.address, self.wallet.address)

	def test_wallet_link(self):
		self.wallet.link(self.secret, self.secondSecret)
		self.assertEqual(dposlib.blockchain.Transaction._publicKey, self.wallet.publicKey)
		self.assertEqual(dposlib.blockchain.Transaction._secondPublicKey, self.wallet.secondPublicKey)

