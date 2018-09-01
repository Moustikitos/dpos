# -*- coding: utf-8 -*-
# © Toons

import os
import json
import dposlib

from collections import OrderedDict

from dposlib import ROOT
from dposlib.blockchain import slots, cfg
from dposlib.util.data import loadJson, dumpJson
from dposlib.util.bin import hexlify


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
		"""Return current registry path."""
		if hasattr(Transaction, "_publicKey"):
			return os.path.join(ROOT, ".registry", cfg.network, Transaction._publicKey)
		else:
			raise Exception("Register a public key or set secret")

	@staticmethod
	def link(secret=None, secondSecret=None):
		"""
		Save public and private keys derived from secrets. This is equivalent to
		wallet login and limits number of secret keyboard entries.
		"""
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
		"""
		Remove public and private keys. This is equivalent to a wellet logout.
		Once keys removed, no signature is possible.
		"""
		for attr in [
			'_privateKey',
			'_publicKey',
			'_secondPublicKey'
			'_secondPrivateKey'
		]:
			if hasattr(Transaction, attr):
				delattr(Transaction, attr)

	@staticmethod
	def setDynamicFee():
		Transaction.DFEES = True

	@staticmethod
	def setStaticFee():
		Transaction.DFEES = False

	@staticmethod
	def load(txid):
		"""Loads the transaction identified by txid from current registry."""
		pathfile = Transaction.path()
		registry = loadJson(pathfile)
		return Transaction(registry[txid])

	def __repr__(self):
		return json.dumps(OrderedDict(sorted(self.items(), key=lambda e:e[0])), indent=2)

	def __init__(self, arg={}, **kwargs):
		dict.__init__(self)

		if "type" not in self:
			self["type"] = 0
		if hasattr(cfg, "begintime") and "timestamp" not in self:
			self["timestamp"] = slots.getTime()

		for key,value in [(k,v) for k,v in dict(arg, **kwargs).items() if v != None]:
			self[key] = value
		if hasattr(Transaction, "_publicKey"):
			dict.__setitem__(self, "senderPublicKey", Transaction._publicKey)

		self.setFees()

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
		# set internal private keys (secrets are not stored)
		elif hasattr(dposlib, "core"):
			if item == "secret":
				Transaction.link(value)
			elif item == "secondSecret":
				Transaction.link(None, value)
			elif item == "privateKey":
				Transaction._privateKey = str(value)
			elif item == "secondPrivateKey":
				Transaction._secondPrivateKey = str(value)

	def setFees(self):
		if Transaction.DFEES:
			dposlib.core.setDynamicFees(self)
		else:
			fee = cfg.fees.get(TRANSACTIONS[self["type"]], False)
			dict.__setitem__(self, "fee", fee)

	def signWithSecret(self, secret):
		Transaction.link(secret)
		self.sign()

	def signSignWithSecondSecret(self, secondSecret):
		Transaction.link(None, secondSecret)
		self.signSign()

	def signWithKeys(self, publicKey, privateKey):
		dict.__setitem__(self, "senderPublicKey", publicKey)
		Transaction._publicKey = publicKey
		Transaction._privateKey = privateKey
		self.sign()

	def signSignWithKey(self, secondPrivateKey):
		Transaction._secondPrivateKey = secondPrivateKey
		self.signSign()

	def sign(self):
		if hasattr(Transaction, "_privateKey"):
			if "senderPublicKey" not in self:
				dict.__setitem__(self, "senderPublicKey", Transaction._publicKey)
			self["signature"] = dposlib.core.crypto.getSignature(self, Transaction._privateKey)
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

	def finalize(self):
		if hasattr(Transaction, "_privateKey"):
			self.sign()
			if hasattr(Transaction, "_secondPrivateKey"):
				self.signSign()
			self.identify()
		else:
			raise Exception("Orphan transaction")
			
	def dump(self):
		"""Dumps transaction in current registry."""
		if "id" in self:
			id_ = self["id"]
			pathfile = Transaction.path()
			registry = loadJson(pathfile)
			registry[self["id"]] = self
			dumpJson(registry, pathfile)
