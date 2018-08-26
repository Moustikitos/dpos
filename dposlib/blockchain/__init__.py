# -*- coding: utf-8 -*-
# © Toons

import dposlib
from dposlib.blockchain import slots, cfg
from dposlib.util.bin import hexlify, unhexlify


class Transaction(dict):

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
		"signature": hexlify,
		"signSignature": hexlify,
		"id": hexlify
	}

	def __init__(self, arg={}, **kwargs):
		dict.__init__(self)

		if "type" not in self:
			self["type"] = 0

		if hasattr(cfg, "begintime") and "timestamp" not in self:
			self["timestamp"] = slots.getTime()

		if hasattr(cfg, "fees") and "fee" not in self: 
			self["fee"] = cfg.fees.get(
				{	0: "send",
					1: "secondsignature",
					2: "delegate",
					3: "vote",
				}[self.get("type", 0)]
			)

		self.update(arg, **kwargs)
		
	def __setitem__(self, item, value):
		if item in Transaction.typing.keys():
			cast = Transaction.typing[item]
			if not isinstance(value, cast):
				value = cast(value)
		if hasattr(dposlib, "core"):
			if item == "secret":
				keys = dposlib.core.getKeys(value)
				dict.__setitem__(self, "publicKey", hexlify(keys["publicKey"]))
				self.__privateKey = hexlify(keys["privateKey"])
			elif item == "secondSecret":
				keys = dposlib.core.getKeys(value)
				self.__secondPrivateKey = hexlify(keys["privateKey"])
			elif item == "privateKey":
				self.__privateKey = hexlify(value)
			elif item == "secondPrivateKey":
				self.__secondPrivateKey = hexlify(value)
		dict.__setitem__(self, item, value)

	def signFromSecret(self, secret):
		keys = dposlib.core.getKeys(secret)
		self["senderPublicKey"] = keys["publicKey"]
		self.__privateKey = keys["privateKey"]
		self.sign()

	def signSignFromSecondSecret(self, secondSecret):
		keys = dposlib.core.getKeys(secondSecret)
		self.__secondPrivateKey = keys["privateKey"]
		self.signSign()

	def signFromKeys(self, publicKey, privateKey):
		self["senderPublicKey"] = publicKey
		self.__privateKey = privateKey
		self.sign()

	def signSignFromKeys(self, secondPrivateKey):
		self.__secondPrivateKey = secondPrivateKey
		self.signSign()

	def sign(self):
		self["signature"] = dposlib.core.getSignature(self, self.__privateKey)

	def signSign(self):
		self["signSignature"] = dposlib.core.getSignature(self, self.__secondPrivateKey)

	def identify(self):
		self["id"] = dposlib.core.getId(self)
