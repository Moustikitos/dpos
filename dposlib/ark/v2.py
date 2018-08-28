# -*- coding: utf-8 -*-
# © Toons

import struct

from collections import OrderedDict

from dposlib import PY3, rest
from dposlib.ark import crypto, init, stop
from dposlib.util.bin import unhexlify, hexlify
from dposlib.blockchain import Transaction, slots, cfg


def computePayload(typ, **kwargs):

	if typ == 0:
		try:
			recipientId = crypto.base58.b58decode_check(kw["recipientId"])
		except:
			raise Exception("no recipientId defined")
		return struct.pack(
			"!QI21s",
			int(kwargs.get("amount", 0)),
			int(kwargs.get("expiration", 0)),
			recipientId
		)

	return b""


def getBytes(tx):
	typ_ = tx.get("type", 0)
	vendorField = tx.get("vendorField", "")
	vendorField = vendorField.encode("utf-8") if not isinstance(vendorField, bytes) else vendorField
	lenVF = len(vendorField)
	payload = computePayload(typ_, **tx)

	tx["fee"] = (typ_ + 50 + lenVF + len(payload)) * Transaction.C

	header = struct.pack(
		"!BBBBI33sQB%ss"%lenVF,
		tx.get("head", 0xff),
		tx.get("version", 0x02),
		tx.get("network", int(cfg.marker, base=16)),
		typ_,
		tx.get("timestamp", slots.getTime()),
		unhexlify(tx._Transaction__publicKey),
		tx["fee"],
		lenVF,
		vendorField.encode("utf-8") if not isinstance(vendorField, bytes) else vendorField
	)

	return header + payload

crypto.getBytes = getBytes


# class Payload(object):

# 	C = 0.0001 * 100000000

# 	@staticmethod
# 	def setArkPerByteFees(value):
# 		Payload.C = value

# 	@staticmethod
# 	def get(typ, **kw):
# 		"""
# 		Return a payload from keyword parameters.
# 		"""
# 		return crypto.hexlify(getattr(Payload, "type%d" % typ)(**kw))

# 	@staticmethod
# 	def type0(**kw):
# 		try:
# 			recipientId = crypto.base58.b58decode_check(kw["recipientId"])
# 		except:
# 			raise Exception("no recipientId defined")
# 		return struct.pack(
# 			"<QI21s",
# 			int(kw.get("amount", 0)),
# 			int(kw.get("expiration", 0)),
# 			recipientId
# 		)

# 	@staticmethod
# 	def type1(**kw):
# 		if "secondSecret" in kw:
# 			secondPublicKey = crypto.getKeys(kw["secondSecret"])["publicKey"]
# 		elif "secondPublicKey" in kw:
# 			secondPublicKey = kw["secondPublicKey"]
# 		else:
# 			raise Exception("no secondSecret or secondPublicKey given")
# 		return struct.pack("<33s", crypto.unhexlify(secondPublicKey))

# 	@staticmethod
# 	def type2(**kw):
# 		username = kw.get("username", False)
# 		if username:
# 			length = len(username)
# 			if 3 <= length <= 255:
# 				return struct.pack("<B%ds" % length, length, username.encode())
# 			else:
# 				raise Exception("bad username length [3-255]: %s" % username)
# 		else:
# 			raise Exception("no username defined")

# 	@staticmethod
# 	def type3(**kw):
# 		delegatePublicKey = kw.get("delegatePublicKey", False)
# 		if delegatePublicKey:
# 			length = len(delegatePublicKey)
# 			return struct.pack("<%ds" % length, delegatePublicKey.encode())
# 		else:
# 			raise Exception("no up/down vote given")

