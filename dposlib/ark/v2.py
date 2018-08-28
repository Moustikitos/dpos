# -*- coding: utf-8 -*-
# © Toons

import struct

from collections import OrderedDict

from dposlib import PY3, rest
from dposlib.ark import crypto, init, stop
from dposlib.util.bin import unhexlify, hexlify
from dposlib.blockchain import Transaction, slots, cfg


def computePayload(typ, **kwargs):

	data = kwargs.get("asset", {})

	if typ == 0:
		try:
			recipientId = crypto.base58.b58decode_check(kwargs["recipientId"])
		except:
			raise Exception("no recipientId defined")
		return struct.pack(
			"!QI21s",
			int(kwargs.get("amount", 0)),
			int(kwargs.get("expiration", 0)),
			recipientId
		)

	elif typ == 1:
		if "secondSecret" in data:
			secondPublicKey = crypto.getKeys(data["secondSecret"])["publicKey"]
		elif "secondPublicKey" in data:
			secondPublicKey = data["secondPublicKey"]
		else:
			raise Exception("no secondSecret or secondPublicKey given")
		return struct.pack("!33s", crypto.unhexlify(secondPublicKey))

	elif typ == 2:
		username = data.get("username", False)
		if username:
			length = len(username)
			if 3 <= length <= 255:
				return struct.pack("!B%ds" % length, length, username.encode())
			else:
				raise Exception("bad username length [3-255]: %s" % username)
		else:
			raise Exception("no username defined")

	elif typ == 3:
		delegatePublicKeys = data.get("delegatePublicKeys", False)
		if delegatePublicKeys:
			length = len(delegatePublicKeys)
			payload = struct.pack("!%ds" % length, length)
			for delegatePublicKey in delegatePublicKeys:
				payload += struct.pack("!34s", delegatePublicKey.encode())
			return payload
		else:
			raise Exception("no up/down vote given")

	elif typ == 4:
		result = struct.pack("!BBB", data.get("minimum", 2), data.get("number", 3), data.get("lifetime", 24))
		for publicKey in data.get("publicKeys"):
			result += struct.pack("!33s", publicKey.encode())
		return payload

	elif typ == 5:
		dag = dara["dag"]
		return struct.pack("!B%ss" % len(dag), dag.encode())

	elif typ == 6:
		try:
			recipientId = crypto.base58.b58decode_check(kwargs["recipientId"])
		except:
			raise Exception("no recipientId defined")
		return struct.pack(
			"!QBI21s",
			int(kwargs.get("amount", 0)),
			int(kwargs.get("type", 0)),
			int(kwargs.get("timelock", 0)),
			recipientId
		)

	elif typ == 7:
		try:
			items = [(amount, crypto.base58.b58decode_check(address)) for amount,address in data.items()]
		except:
			raise Exception("error in recipientId address list")
		result = struct.pack("!H", len(items)):
		for amount,address in items:
			result += struct.pack("!B21s", amount, address)
		return result

	elif typ == 8:
		return b""

	else:
		raise Exception("Unknown transaction type %d" % typ)


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


##### INTERFACE ######

def send(amount, address, vendorField=None):
	pass


def registerSecondSecret(secondSecret):
	pass


def registerSecondPublicKey(secondPublicKey):
	pass


def registerAsDelegate(username):
	pass


def upVote(*usernames):
	pass


def downVote(*usernames):
	pass


# erase old definitions
crypto.getBytes = getBytes
dposlib.ark.send = send
dposlib.ark.registerSecondSecret = registerSecondSecret
dposlib.ark.registerSecondPublicKey = registerSecondPublicKey
dposlib.ark.registerAsDelegate = registerAsDelegate
dposlib.ark.upVote = upVote
dposlib.ark.downVote = downVote
