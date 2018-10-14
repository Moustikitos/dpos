# -*- coding: utf-8 -*-
# © Toons

import struct

from dposlib import ROOT, rest
from dposlib.ark import crypto
from dposlib.blockchain import Transaction, slots, cfg
from dposlib.util.bin import unhexlify, hexlify
from dposlib.util.data import loadJson, dumpJson
	

def computePayload(typ, tx):

	data = tx.get("asset", {})
	if data == {}: data = tx

	if typ == 0:
		try:
			recipientId = crypto.base58.b58decode_check(data["recipientId"])
		except:
			raise Exception("no recipientId defined")
		return struct.pack(
			"<QI21s",
			int(data.get("amount", 0)),
			int(data.get("expiration", 0)),
			recipientId
		)

	elif typ == 1:
		if "signature" in data:
			secondPublicKey = data["signature"]["publicKey"]
		else:
			raise Exception("no secondSecret or secondPublicKey given")
		return struct.pack("<33s", crypto.unhexlify(secondPublicKey))

	elif typ == 2:
		username = data.get("delegate", {}).get("username", False)
		if username:
			length = len(username)
			if 3 <= length <= 255:
				return struct.pack("<B%ds" % length, length, username.encode())
			else:
				raise Exception("bad username length [3-255]: %s" % username)
		else:
			raise Exception("no username defined")

	elif typ == 3:
		delegatePublicKeys = data.get("votes", False)
		if delegatePublicKeys:
			length = len(delegatePublicKeys)
			payload = struct.pack("<B", length)
			for delegatePublicKey in delegatePublicKeys:
				delegatePublicKey = delegatePublicKey.replace("+", "01").replace("-", "00")
				payload += struct.pack("<34s", delegatePublicKey.encode())
			return payload
		else:
			raise Exception("no up/down vote given")

	elif typ == 4:
		result = struct.pack("<BB", data.get("minimum", 2), data.get("number", 3))
		for publicKey in data.get("publicKeys"):
			result += struct.pack("<33s", publicKey.encode())
		return payload

	elif typ == 5:
		dag = dara["dag"]
		return struct.pack("<B%ss" % len(dag), dag.encode())

	elif typ == 6:
		try:
			recipientId = crypto.base58.b58decode_check(kwargs["recipientId"])
		except:
			raise Exception("no recipientId defined")
		return struct.pack(
			"<QBI21s",
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
		result = struct.pack("<H", len(items))
		for amount,address in items:
			result += struct.pack("<B21s", amount, address)
		return result

	elif typ == 8:
		return b""

	else:
		raise Exception("Unknown transaction type %d" % typ)


def getBytes(tx):
	typ = tx.get("type", 0)
	vendorField = tx.get("vendorField", "")
	vendorField = vendorField.encode("utf-8") if not isinstance(vendorField, bytes) else vendorField

	header = struct.pack(
		"<BBBBI33sQB",
		tx.get("head", 0xff),
		tx.get("version", 0x02),
		tx.get("network", int(cfg.marker, base=16)),
		typ,
		tx.get("timestamp", slots.getTime()),
		unhexlify(Transaction._publicKey),
		tx["fee"],
		len(vendorField)
	)
	
	payload = computePayload(typ, tx)

	return header + vendorField + payload


def createWebhook(peer, event, target, conditions, folder=None):
	data = rest.POST.api.webhooks(peer=peer, event=event, target=target, conditions=conditions, returnKey="data")
	if "token" in data:
		dumpJson(data, os.path.join(ROOT if not folder else folder, "%s.whk" % data["token"]))
	return data


def deleteWebhook(peer, id, token=None):
	rest.DELETE.api.webhooks("%s"%id, peer=peer, token=token)
