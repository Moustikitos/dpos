# -*- coding: utf-8 -*-
# © Toons

import os
import dposlib

from dposlib import ROOT
from dposlib.blockchain import slots, cfg
from dposlib.util.data import loadJson, dumpJson


class Transaction(dict):

	DFEES = False
	FMULT = 10000

	typing = {
		"timestamp": int,
		"type": int,
		"amount": int,
		"senderPublicKey": str,
		"recipientId": str,
		"senderId": str,
		"vendorField": str,
		"asset": dict,
		"signature": str,
		"signSignature": str,
		"id": str
	}

	@staticmethod
	def path():
		if hasattr(Transaction, "_publicKey"):
			return os.path.join(ROOT, ".registry", cfg.network, Transaction._publicKey)
		else:
			raise Exception("Register Public key or set secret")

	@staticmethod
	def link(secret=None, secondSecret=None):
		if hasattr(dposlib, "core"):
			if secret:
				keys = dposlib.core.crypto.getKeys(secret)
				Transaction._publicKey = keys["publicKey"]
				Transaction._privateKey = keys["privateKey"]
			if secondSecret:
				keys = dposlib.core.crypto.getKeys(secondSecret)
				Transaction._secondPublicKey = keys["publicKey"]
				Transaction._secondPrivateKey = keys["privateKey"]

	@staticmethod
	def unlink():
		for attr in [
			'_privateKey',
			'_publicKey',
			'_secondPublicKey'
			'_secondPrivateKey'
		]:
			if hasattr(Transaction, attr):
				delattr(Transaction, attr)

	@staticmethod
	def setDynamicFee(value):
		Transaction.FMULT = value

	@staticmethod
	def load(txid):
		pathfile = Transaction.path()
		registry = loadJson(pathfile)
		return Transaction(registry[txid])

	def __init__(self, arg={}, **kwargs):
		dict.__init__(self)

		if "type" not in self:
			self["type"] = 0

		if hasattr(cfg, "begintime") and "timestamp" not in self:
			self["timestamp"] = slots.getTime()

		for key,value in [(k,v) for k,v in dict(arg, **kwargs).items() if v != None]:
			self[key] = value

		if not Transaction.DFEES:
			dict.__setitem__(self, "fee", cfg.fees.get(
				{	0: "send",
					1: "secondsignature",
					2: "delegate",
					3: "vote",
					4: "multisignature",
					5: "dapp"
				}[self.get("type", 0)]
			))

		if hasattr(Transaction, "_publicKey"):
			dict.__setitem__(self, "senderPublicKey", Transaction._publicKey)

	def __getitem__(self, item):
		if item in ["senderPublicKey", "publicKey"]:
			return self._publicKey
		else:
			return dict.__getitem__(self, item)

	def __setitem__(self, item, value):
		# cast values according to transaction typing
		if item in Transaction.typing.keys():
			cast = Transaction.typing[item]
			if not isinstance(value, cast):
				value = cast(value)

			dict.__setitem__(self, item, value)

			if item not in ["signature", "signSignature", "id"]:
				self.pop("signature", False)
				self.pop("signSignature", False)
				self.pop("id", False)
		# set internal private keys (secret are not stored)
		elif hasattr(dposlib, "core"):
			if item == "secret":
				Transaction.link(value)
				dict.__setitem__(self, "senderPublicKey", Transaction._publicKey)
			elif item == "secondSecret":
				Transaction.link(None, value)
			elif item == "privateKey":
				Transaction._privateKey = str(value)
			elif item == "secondPrivateKey":
				Transaction._secondPrivateKey = str(value)

	def signFromSecret(self, secret):
		keys = dposlib.core.crypto.getKeys(secret)
		self["senderPublicKey"] = keys["publicKey"]
		Transaction._publicKey = keys["publicKey"]
		Transaction._privateKey = keys["privateKey"]
		self.sign()

	def signSignFromSecondSecret(self, secondSecret):
		keys = dposlib.core.crypto.getKeys(secondSecret)
		Transaction._secondPublicKey = keys["publicKey"]
		Transaction._secondPrivateKey = keys["privateKey"]
		self.signSign()

	def signFromKeys(self, publicKey, privateKey):
		self["senderPublicKey"] = publicKey
		Transaction._publicKey = publicKey
		Transaction._privateKey = privateKey
		self.sign()

	def signSignFromKey(self, secondPrivateKey):
		Transaction._secondPrivateKey = secondPrivateKey
		self.signSign()

	def sign(self):
		if "senderPublicKey" in self:
			try:
				self["signature"] = dposlib.core.crypto.getSignature(self, Transaction._privateKey)
			except AttributeError:
				raise Exception("No private Key available")
		else:
			raise Exception("Orphan transaction can not sign itsef")

	def signSign(self):
		if "signature" in self:
			try:
				self["signSignature"] = dposlib.core.crypto.getSignature(self, Transaction._secondPrivateKey)
			except AttributeError:
				raise Exception("No second private Key available")
		else:
			raise Exception("Transaction not signed")

	def identify(self):
		if "signature" in self:
			self["id"] = dposlib.core.crypto.getId(self)
		else:
			raise Exception("Transaction not signed")

	def dump(self):
		"""Write transaction in a registry"""
		if "id" in self:
			id_ = self["id"]
			pathfile = Transaction.path()
			registry = loadJson(pathfile)
			registry[self["id"]] = self
			dumpJson(registry, pathfile)

