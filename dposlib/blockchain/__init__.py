# -*- coding: utf-8 -*-
# © Toons

import dposlib
from dposlib.blockchain import slots, cfg


class Transaction(dict):

	C = 0.0001 * 100000000

	typing = {
		"timestamp": int,
		"type": int,
		"amount": int,
		"fee": int,
		"senderPublicKey": str,
		"recipientId": str,
		"senderId": str,
		"vendorField": str,

		"asset": dict,
		"payload": dict,

		"signature": str,
		"signSignature": str,
		"id": str
	}

	@staticmethod
	def link(secret=None, secondSecret=None):
		if hasattr(dposlib, "core"):
			if secret:
				keys = dposlib.core.crypto.getKeys(secret)
				Transaction.__publicKey = keys["publicKey"]
				Transaction.__privateKey = keys["privateKey"]
			if secondSecret:
				keys = dposlib.core.crypto.getKeys(secondSecret)
				Transaction.__secondPrivateKey = keys["privateKey"]

	@staticmethod
	def unlink():
		for attr in [
			'_Transaction__privateKey',
			'_Transaction__publicKey',
			'_Transaction__secondPrivateKey'
		]:
			if hasattr(Transaction, attr):
				delattr(Transaction, attr)

	@staticmethod
	def setDynamicFee(value):
		Transaction.C = value * 100000000

	def __init__(self, arg={}, **kwargs):
		dict.__init__(self)

		if "type" not in self:
			self["type"] = 0

		if hasattr(cfg, "begintime") and "timestamp" not in self:
			self["timestamp"] = slots.getTime()

		for key,value in dict(arg, **kwargs).items():
			self[key] = value

		if hasattr(cfg, "fees") and "fee" not in self: 
			self["fee"] = cfg.fees.get(
				{	0: "send",
					1: "secondsignature",
					2: "delegate",
					3: "vote",
					4: "multisignature",
					5: "dapp"
				}[self.get("type", 0)]
			)
		
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
		if hasattr(dposlib, "core"):
			if item == "secret":
				Transaction.link(value)
				dict.__setitem__(self, "senderPublicKey", Transaction.__publicKey)
			elif item == "secondSecret":
				Transaction.link(None, value)
			elif item == "privateKey":
				Transaction.__privateKey = str(value)
			elif item == "secondPrivateKey":
				Transaction.__secondPrivateKey = str(value)

	def signFromSecret(self, secret):
		keys = dposlib.core.crypto.getKeys(secret)
		self["senderPublicKey"] = keys["publicKey"]
		Transaction.__privateKey = keys["privateKey"]
		self.sign()

	def signSignFromSecondSecret(self, secondSecret):
		keys = dposlib.core.crypto.getKeys(secondSecret)
		Transaction.__secondPrivateKey = keys["privateKey"]
		self.signSign()

	def signFromKeys(self, publicKey, privateKey):
		self["senderPublicKey"] = publicKey
		Transaction.__privateKey = privateKey
		self.sign()

	def signSignFromKey(self, secondPrivateKey):
		Transaction.__secondPrivateKey = secondPrivateKey
		self.signSign()

	def sign(self):
		if "senderPublicKey" in self:
			try:
				self["signature"] = dposlib.core.crypto.getSignature(self, Transaction.__privateKey)
			except AttributeError:
				raise Exception("No private Key available")
		else:
			raise Exception("Orphan transaction can not sign itsef")

	def signSign(self):
		if "signature" in self:
			try:
				self["signSignature"] = dposlib.core.crypto.getSignature(self, Transaction.__secondPrivateKey)
			except AttributeError:
				raise Exception("No second private Key available")
		else:
			raise Exception("Transaction not signed")

	def identify(self):
		if "signature" in self:
			self["id"] = dposlib.core.crypto.getId(self)
		else:
			raise Exception("Transaction not signed")
