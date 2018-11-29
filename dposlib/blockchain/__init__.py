# -*- coding: utf-8 -*-
# © Toons

import os
import json
import dposlib
import weakref

from collections import OrderedDict

from dposlib import ROOT
from dposlib.blockchain import slots, cfg
from dposlib.util.asynch import setInterval
from dposlib.util.data import loadJson, dumpJson
from dposlib.util.bin import hexlify


def track_data(value=True):
	Data.TRACK = value


class Transaction(dict):

	DFEES = False
	FMULT = 10000
	FEESL = None

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
			'_secondPublicKey',
			'_secondPrivateKey'
		]:
			if hasattr(Transaction, attr):
				delattr(Transaction, attr)

	@staticmethod
	def setDynamicFee(value="avgFee"):
		"""
		Activate and configure dynamic fees parameters. Value can be either an
		integer defining the fee multiplier constant or a string defining the
		fee level to use acccording to the 30-days-average. possible values are
		'avgFee' (default) 'minFee' and 'maxFee'.
		"""
		if hasattr(cfg, "doffsets"):
			Transaction.DFEES = True
			if isinstance(value, int):
				Transaction.FMULT = value
				Transaction.FEESL = None
			elif value in ["maxFee", "avgFee", "minFee"]:
				Transaction.FEESL = value
		else:
			raise Exception("Dynamic fees can not be set on %s network" % cfg.network)

	@staticmethod
	def setStaticFee():
		"""Activate static fees."""
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
		data = dict(arg, **kwargs)
		dict.__init__(self)
		
		self["type"] = data.pop("type", 0) # default type is 0 (transfer)
		self["timestamp"] = data.pop("timestamp", slots.getTime()) # set timestamp if no one given
		self["asset"] = data.pop("asset", {}) # put asset value if no one given
		for key,value in [(k,v) for k,v in data.items() if v != None]:
			self[key] = value

		if hasattr(Transaction, "_publicKey"):
			dict.__setitem__(self, "senderPublicKey", Transaction._publicKey)

	def __setitem__(self, item, value):
		# cast values according to transaction typing
		if item in dposlib.core.TYPING.keys():
			cast = dposlib.core.TYPING[item]
			if not isinstance(value, cast):
				value = cast(value)
			dict.__setitem__(self, item, value)
			# remove signatures and ids if an item other than signature or id is modified
			if item not in ["signature", "signatures", "signSignature", "id"]:
				self.pop("signature", False)
				self.pop("signatures", False)
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
			# use 30-days-average id FEESL is not None
			if Transaction.FEESL != None:
				fee = cfg.feestats[self["type"]][Transaction.FEESL]
			# else compute fees using fee multiplier and tx size
			else:
				fee = dposlib.core.computeDynamicFees(self)
		else:
			# k is 0 or signature number in case of multisignature tx
			k = len(self.get("asset", {}).get("multisignature", {}).get("keysgroup", []))
			fee = cfg.fees["staticFees"].get(dposlib.core.TRANSACTIONS[self["type"]]) * (1+k)
		dict.__setitem__(self, "fee", fee)

	def feeIncluded(self):
		if self["type"] in [0, 7] and self["fee"] < self["amount"]:
			if not hasattr(self, "_amount"):
				setattr(self, "_amount", self["amount"])
			self["amount"] = self._amount - self["fee"]

	def feeExcluded(self):
		if self["type"] in [0, 7] and hasattr(self, "_amount"):
			self["amount"] = self._amount
			delattr(self, "_amount")

	# sign functions using passphrases
	def signWithSecret(self, secret):
		Transaction.link(secret)
		self.sign()

	def signSignWithSecondSecret(self, secondSecret):
		Transaction.link(None, secondSecret)
		self.signSign()

	def multiSignWithSecret(self, secret):
		self.multiSignWithKey(dposlib.core.crypto.getKeys(secret)["privateKey"])

	# sign function using crypto keys
	def signWithKeys(self, publicKey, privateKey):
		dict.__setitem__(self, "senderPublicKey", publicKey)
		Transaction._publicKey = publicKey
		Transaction._privateKey = privateKey
		self.sign()

	def signSignWithKey(self, secondPrivateKey):
		Transaction._secondPrivateKey = secondPrivateKey
		self.signSign()

	def multiSignWithKey(self, privateKey):
		signature = dposlib.core.crypto.getSignature(self, privateKey)
		if "signatures" in self:
			self["signatures"].append(signature)
		else:
			self["signatures"] = [signature]

	# root sign function called by others
	def sign(self):
		if hasattr(Transaction, "_privateKey"):
			address = dposlib.core.crypto.getAddress(Transaction._publicKey)
			dict.__setitem__(self, "senderPublicKey", Transaction._publicKey)
			if "senderId" not in self:
				self["senderId"] = address
			if self["type"] in [1, 3, 4] and "recipientId" not in self:
				self["recipientId"] = address
			self["signature"] = dposlib.core.crypto.getSignature(self, Transaction._privateKey)
		else:
			raise Exception("Orphan transaction can not sign itsef")

	# root second sign function called by others
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

	def finalize(self, secret=None, secondSecret=None, fee_included=False):
		"""
		Finalize a transaction by setting fees, signatures and id.
		"""
		Transaction.link(secret, secondSecret)
		self.setFees()
		if fee_included:
			self.feeIncluded()
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


class Data:

	REF = set()
	EVENT = False
	TRACK = True

	@setInterval(30)
	def heartbeat():
		for ref in list(Data.REF):
			dead, obj = set(), ref()
			if obj:
				obj.update()
			else:
				dead.add(ref)	
		Data.REF -= dead

		if len(Data.REF) == 0:
			Data.EVENT.set()
			Data.EVENT = False
	
	def __init__(self, endpoint, *args, **kwargs):
		track = kwargs.pop("track", Data.TRACK)
		self.__dict = dict(**endpoint(*args, **kwargs))
		self.__endpoint = endpoint
		self.__kwargs = kwargs
		self.__args = args

		if Data.EVENT == False:
			Data.EVENT = Data.heartbeat()
		if track:
			self.track()

	def __repr__(self):
		return json.dumps(OrderedDict(sorted(self.__dict.items(), key=lambda e:e[0])), indent=2)

	def __getattr__(self, attr):
		return self.__dict[attr]

	def update(self):
		result = self.__endpoint(*self.__args, **self.__kwargs)
		if "error" not in result:
			self.__dict.update(**result)

	def track(self):
		Data.REF.add(weakref.ref(self))
