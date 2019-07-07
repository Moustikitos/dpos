# -*- coding: utf-8 -*-
# © Toons

import os
import sys
import json
import unittest
import dposlib

from dposlib import rest

def connection_enabled(func):
	def wrapper(*args, **kw):
		if rest.cfg.hotmode:
			return func(*args, **kw)
	return wrapper


class TestDposApi(unittest.TestCase):

	@classmethod
	def setUpClass(self):
		# secrets used for testing
		self.secret = "secret"
		self.secondSecret = "secondSecret"
		# initialize on ark devnet
		if rest.use("d.ark"):
			self.wallet = dposlib.core.api.Wallet(
				dposlib.core.crypto.getAddress(dposlib.core.crypto.getKeys(self.secret)["publicKey"])
			)

	def test_networks(self):
		path = os.path.join(dposlib.ROOT, "network")
		for name in [n.replace(".net", "") for n in os.listdir(path) if n.endswith(".net")]:
			try:
				self.assertEqual(rest.use(name), True)
			except Exception as e:
				sys.stdout.write("%s network failed...\n" % name)
			# else:
			# 	try:
			# 		print("%s (blocktime=%s)" % (rest.cfg.network, rest.cfg.blocktime), json.dumps(dposlib.core.mixin.deltas(), indent=2))
			# 	except:
			# 		pass
		rest.use("d.ark")

	@connection_enabled
	def test_wallet(self):
		wlt = dposlib.core.api.Wallet(self.wallet.username)
		self.assertEqual(wlt.address, self.wallet.address)

	@connection_enabled
	def test_wallet_link(self):
		self.wallet.link(self.secret, self.secondSecret)
		self.assertEqual(dposlib.blockchain.Transaction._publicKey, self.wallet.publicKey)
		self.assertEqual(dposlib.blockchain.Transaction._secondPublicKey, self.wallet.secondPublicKey)
