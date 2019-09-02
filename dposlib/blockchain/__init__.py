# -*- coding: utf-8 -*-
# © Toons
"""
"""

import os
import sys
import json
import dposlib
import weakref
import getpass

from collections import OrderedDict

from dposlib import rest
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

	def _setSenderPublicKey(self, publicKey):
		dict.__setitem__(self, "senderPublicKey", publicKey)
		if self._version >= 0x02:
			# TODO: setNonce
			pass
		elif "timestamp" not in self:
			self["timestamp"] = slots.getTime() # set timestamp

	@staticmethod
	def path():
		"""Return current registry path."""
		if hasattr(Transaction, "_publicKey"):
			return os.path.join(dposlib.ROOT, ".registry", cfg.network, Transaction._publicKey)
		else:
			raise Exception("No public key found")

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
	def useDynamicFee(value="avgFee"):
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
	setDynamicFee = useDynamicFee

	@staticmethod
	def useStaticFee():
		"""Activate static fees."""
		Transaction.DFEES = False
	setStaticFee = useStaticFee

	@staticmethod
	def load(txid):
		"""Loads the transaction identified by txid from current registry."""
		data = loadJson(Transaction.path())[txid]
		data["senderId"] = dposlib.core.crypto.getAddress(data["senderPublicKey"], marker=data.pop("network", False))
		return Transaction(data)

	def __repr__(self):
		return json.dumps(OrderedDict(sorted(self.items(), key=lambda e:e[0])), indent=2)

	def __init__(self, arg={}, **kwargs):
		self.__dict__["_version"] = kwargs.pop("version", 0x01)
		if not hasattr(dposlib, "core"):
			raise Exception("no blockchain loaded")
		data = dict(arg, **kwargs)
		dict.__init__(self)

		self["amount"] = data.pop("amount", 0) # amount is required field
		self["type"] = data.pop("type", 0) # default type is 0 (transfer)
		self["asset"] = data.pop("asset", {}) # put asset value if no one given
		if self._version >= 0x02:
			self["typeGroup"] = data.pop("typeGroup", 1) # default typeGroup is 1 (Ark core)

		for key,value in [(k,v) for k,v in data.items() if v != None]:
			self[key] = value

		if hasattr(Transaction, "_publicKey"):
			self._setSenderPublicKey(Transaction._publicKey)

	def __setitem__(self, item, value):
		# cast values according to transaction typing
		if item in dposlib.core.TYPING.keys():
			cast = dposlib.core.TYPING[item]
			if not isinstance(value, cast):
				value = cast(value)
			dict.__setitem__(self, item, value)
			# remove signatures and ids if an item other than signature or id is modified
			if item not in ["signature", "signSignature", "secondSignature", "id"]:
				self.pop("signature", False)
				self.pop("signSignature", False)
				self.pop("secondSignature", False)
				self.pop("id", False)
		# set internal private keys (secrets are not stored)
		elif hasattr(dposlib, "core"):
			if item == "secret":
				Transaction.link(value)
				self._setSenderPublicKey(Transaction._publicKey)
			elif item == "secondSecret":
				Transaction.link(None, value)
			elif item == "privateKey":
				Transaction._privateKey = str(value)
			elif item == "secondPrivateKey":
				Transaction._secondPrivateKey = str(value)
			else:
				raise AttributeError("field '%s' not allowed in '%s' class" % (item, self.__class__.__name__))
		else:
			raise Exception("no blockchain package loaded")

	def __getattr__(self, attr):
		attr = dict.get(self, attr, self.__dict__.get(attr, False))
		if attr == False:
			raise AttributeError("'%s' object has no field '%s'" % (self.__class__.__name__, attr))
		else:
			return attr

	def __setattr__(self, attr, value):
		self[attr] = value

	def setFees(self, value=None):
		if value:
			fee = value
		else:
			static_value = getattr(cfg, "fees", {})\
			               .get("staticFees", getattr(cfg, "fees", {}))\
						   .get(dposlib.core.TRANSACTIONS[self["type"]], 10000000)
			if Transaction.DFEES:
				# use fee statistics if FEESL is not None
				if Transaction.FEESL != None:
					# if fee statistics not found, return static fee value
					fee = cfg.feestats.get(self["type"], {}).get(Transaction.FEESL, static_value)
				# else compute fees using fee multiplier and tx size
				else:
					fee = dposlib.core.computeDynamicFees(self)
			else:
				# k is 0 or signature number in case of multisignature registration
				k = len(self.get("asset", {}).get("multisignature", {}).get("publicKeys", []))
				fee = static_value * (1+k)
		dict.__setitem__(self, "fee", fee)

	def feeIncluded(self):
		if self["type"] in [0, 7] and self["fee"] < self["amount"]:
			if "_amount" not in self.__dict__:
				self.__dict__["_amount"] = self["amount"]
			self["amount"] = self.__dict__["_amount"] - self["fee"]

	def feeExcluded(self):
		if self["type"] in [0, 7] and "_amount" in self.__dict__:
			self["amount"] = self.__dict__["_amount"]
			self.__dict__.pop("_amount", False)

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
			self._setSenderPublicKey(Transaction._publicKey)
			self["senderId"] = address
			if self["type"] in [1, 3, 4, 9] and "recipientId" not in self:
				self["recipientId"] = address
			self["signature"] = dposlib.core.crypto.getSignature(self, Transaction._privateKey)
		else:
			raise Exception("orphan transaction can not sign itsef")

	# root second sign function called by others
	def signSign(self):
		if "signature" in self:
			try:
				self["signSignature"] = dposlib.core.crypto.getSignature(self, Transaction._secondPrivateKey)
			except AttributeError:
				raise Exception("no second private Key available")
		else:
			raise Exception("transaction not signed")

	def identify(self):
		if "signature" in self:
			self["id"] = dposlib.core.crypto.getId(self)
		else:
			raise Exception("transaction not signed")

	def finalize(self, secret=None, secondSecret=None, fee=None, fee_included=False):
		"""
		Finalize a transaction by setting fees, signatures and id.
		"""
		Transaction.link(secret, secondSecret)
		if "fee" not in self or fee != None:
			self.setFees(fee)
		self.feeIncluded() if fee_included else self.feeExcluded()
		self.sign()
		if hasattr(Transaction, "_secondPrivateKey"):
			self.signSign()
		self.identify()

	def dump(self):
		"""Dumps transaction in current registry."""
		if "id" in self:
			id_ = self["id"]
			pathfile = Transaction.path()
			data = dict(self)
			data.pop("senderId", False)
			data.pop("signature", False)
			data.pop("signSignature", False)
			data.pop("id", False)
			data["network"] = int(dposlib.rest.cfg.marker, base=16)
			registry = loadJson(pathfile)
			registry[id_] = data
			dumpJson(registry, pathfile)


###### API
class Data:

	REF = set()
	EVENT = False
	TRACK = True

	@staticmethod
	def wallet_islinked(func):
		def wrapper(*args, **kw):
			obj = args[0]
			if hasattr(obj, "derivationPath"):
				return func(*args, **kw)
			elif not hasattr(obj, "address"):
				raise Exception("not a wallet")
			elif (obj.publicKey == None and dposlib.core.crypto.getAddress(getattr(Transaction, "_publicKey", " ")) == obj.address) or \
			     (getattr(Transaction, "_publicKey", None) == obj.publicKey and getattr(Transaction, "_secondPublicKey", None) == obj.secondPublicKey):
				return func(*args, **kw)
			else:
				raise Exception("wallet not linked yet or publicKey mismatch")
		return wrapper

	@setInterval(30)
	def heartbeat(self):
		dead = set()
		for ref in list(Data.REF):
			obj = ref()
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
		self.__endpoint = endpoint
		self.__kwargs = kwargs
		self.__args = args
		self.__dict = self._get_result()

		if Data.EVENT == False:
			Data.EVENT = self.heartbeat()
		if track:
			self.track()

	def __repr__(self):
		return json.dumps(OrderedDict(sorted(self.__dict.items(), key=lambda e:e[0])), indent=2)

	def __getattr__(self, attr):
		if attr in self.__dict:
			return self.__dict[attr]
		else:
			try: return Data.__getattribute__(attr)
			except: return None

	def _get_result(self):
		if dposlib.rest.cfg.familly == "lisk.v10":
			result = self.__endpoint(*self.__args, **self.__kwargs)
			if isinstance(result, list):
				return result[0]
			elif isinstance(result, dict):
				return result
		else:
			return self.__endpoint(*self.__args, **self.__kwargs)

	def update(self):
		result = self._get_result()
		for key in [k for k in self.__dict if k not in result]:
			self.__dict.pop(key, False)
		self.__dict.update(**result)

	def track(self):
		try:
			Data.REF.add(weakref.ref(self))
		except:
			pass


class Wallet(Data):

	unlink = staticmethod(Transaction.unlink)

	def link(self, secret=None, secondSecret=None):
		self.unlink()
		try:
			keys = dposlib.core.crypto.getKeys(
				secret if secret != None else \
				getpass.getpass("secret > ")
			)
			if self.publicKey == None: # uncreated wallet
				while dposlib.core.crypto.getAddress(keys.get("publicKey", None)) != self.address:
					keys = dposlib.core.crypto.getKeys(getpass.getpass("secret > "))
			else:
				while keys.get("publicKey", None) != self.publicKey:
					keys = dposlib.core.crypto.getKeys(getpass.getpass("secret > "))

			if self.secondPublicKey != None:
				keys_2 = dposlib.core.crypto.getKeys(
					secondSecret if secondSecret != None else \
					getpass.getpass("second secret > ")
				)
				while keys_2.get("publicKey", None) != self.secondPublicKey:
					keys_2 = dposlib.core.crypto.getKeys(getpass.getpass("second secret > "))
			else:
				keys_2 = {}

		except KeyboardInterrupt:
			sys.stdout.write("\n")
			return False

		else:
			Transaction._publicKey = keys["publicKey"]
			Transaction._privateKey = keys["privateKey"]
			if len(keys_2):
				Transaction._secondPublicKey = keys_2["publicKey"]
				Transaction._secondPrivateKey = keys_2["privateKey"]
			return True

	def setFeeLevel(self, fee_level=None):
		if fee_level == None:
			Transaction.useStaticFee()
		else:
			Transaction.useDynamicFee(fee_level)

	def _finalizeTx(self, tx, fee=None, fee_included=False):
		tx.finalize(fee=fee, fee_included=fee_included)
		return tx

	@Data.wallet_islinked
	def send(self, amount, address, vendorField=None, fee_included=False):
		tx = dposlib.core.transfer(amount, address, vendorField)
		return dposlib.core.broadcastTransactions(self._finalizeTx(tx, fee_included=fee_included))

	@Data.wallet_islinked
	def registerSecondSecret(self, secondSecret):
		tx = dposlib.core.registerSecondSecret(secondSecret)
		return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

	@Data.wallet_islinked
	def registerSecondPublicKey(self, secondPublicKey):
		tx = dposlib.core.registerSecondPublicKey(secondPublicKey)
		return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

	@Data.wallet_islinked
	def registerAsDelegate(self, username):
		tx = dposlib.core.registerAsDelegate(username)
		return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

	@Data.wallet_islinked
	def upVote(self, *usernames):
		tx = dposlib.core.upVote(*usernames)
		return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

	@Data.wallet_islinked
	def downVote(self, *usernames):
		tx = dposlib.core.downVote(*usernames)
		return dposlib.core.broadcastTransactions(self._finalizeTx(tx))


try:
	from dposlib import ldgr
except:
	pass
else:
	class NanoS(Wallet):

		def _finalizeTx(self, tx, fee=None, fee_included=False):
			if "fee" not in tx or fee != None:
				tx.setFees(fee)
			tx.feeIncluded() if fee_included else tx.feeExcluded()

			tx["senderId"] = self.address
			if tx["type"] in [1, 3, 4] and "recipientId" not in tx:
				tx["recipientId"] = self.address

			try:
				ldgr.signTransaction(tx, self.derivationPath, self.debug)
			except ldgr.ledgerblue.commException.CommException:
				raise Exception("transaction cancelled")
			
			if self.secondPublicKey != None:
				try:
					keys_2 = dposlib.core.crypto.getKeys(getpass.getpass("second secret > "))
					while keys_2.get("publicKey", None) != self.secondPublicKey:
						keys_2 = dposlib.core.crypto.getKeys(getpass.getpass("second secret > "))
				except KeyboardInterrupt:
					raise Exception("transaction cancelled")
				else:
					tx["signSignature"] = dposlib.core.crypto.getSignature(tx, keys_2["privateKey"])

			tx.identify()
			return tx
