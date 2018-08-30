# -*- coding: utf-8 -*-
# © Toons

import dposlib
import struct

from datetime import datetime
from collections import OrderedDict

import pytz

from dposlib import PY3, rest
from dposlib.ark import crypto
from dposlib.blockchain import Transaction, slots, cfg
from dposlib.util.bin import unhexlify, hexlify
from dposlib.util.asynch import setInterval

from dposlib.ark import stop as _stop
	

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
			payload = struct.pack("!B", length)
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
		result = struct.pack("!H", len(items))
		for amount,address in items:
			result += struct.pack("!B21s", amount, address)
		return result

	elif typ == 8:
		return b""

	else:
		raise Exception("Unknown transaction type %d" % typ)

_getBytes = crypto.getBytes

def getBytes(tx):
	typ_ = tx.get("type", 0)
	vendorField = tx.get("vendorField", "")
	vendorField = vendorField.encode("utf-8") if not isinstance(vendorField, bytes) else vendorField
	lenVF = len(vendorField)
	payload = computePayload(typ_, **tx)

	if "fee" not in tx:
		T = cfg.fees[{
			0: "transfer",
			1: "delegateRegistration",
			2: "secondSignature",
			3: "vote",
			4: "multiSignature",
			5: "ipfs",
			6: "timelockTransfer",
			7: "multiPayment",
			8: "delegateResignation",
		}[tx.get("type", 0)]]
		dict.__setitem__(tx, "fee", (T + 50 + lenVF + len(payload)) * Transaction.FMULT)

	header = struct.pack(
		"!BBBBI33sQB%ss" % lenVF,
		tx.get("head", 0xff),
		tx.get("version", 0x02),
		tx.get("network", int(cfg.marker, base=16)),
		typ_,
		tx.get("timestamp", slots.getTime()),
		unhexlify(Transaction._publicKey),
		tx["fee"],
		lenVF,
		vendorField.encode("utf-8") if not isinstance(vendorField, bytes) else vendorField
	)

	return header + payload


def send(amount, address, vendorField=None):
	return Transaction(
		type=0,
		amount=amount*100000000,
		recipientId=address,
		vendorField=vendorField,
	)


def registerSecondSecret(secondSecret):
	return registerSecondPublicKey(crypto.getKeys(secondSecret)["publicKey"])

def registerSecondPublicKey(secondPublicKey):
	return Transaction(
		type=1,
		asset={"secondPublicKey":secondPublicKey},
	)


def registerAsDelegate(username):
	return Transaction(
		type=2,
		asset={
			"username":username
		},
	)


def upVote(*usernames):
	return Transaction(
		type=3,
		asset={
			"delegatePublicKeys":["01"+rest.GET.api.delegates.get(username=username, returnKey="delegate")["publicKey"] for username in usernames]
		},
	)


def downVote(*usernames):
	return Transaction(
		type=3,
		asset={
			"delegatePublicKeys":["00"+rest.GET.api.delegates.get(username=username, returnKey="delegate")["publicKey"] for username in usernames]
		},
	)


def select_peers():
	peers = [
		"http://%(ip)s:%(port)s" % {
			"ip":p["ip"],
			"port":cfg.ports["@arkecosystem/core-api"]
		} for p in rest.GET.api.peers().get("data", [])][:cfg.broadcast]
	if len(peers):
		cfg.peers = peers


@setInterval(30)
def rotate_peers():
	select_peers()


def init():
	global DAEMON_PEERS
	Transaction.DFEES = True

	data = rest.GET.api.node.configuration().get("data", {})

	constants =  data["constants"]
	cfg.blocktime = constants["blocktime"]
	cfg.begintime = pytz.utc.localize(datetime.strptime(constants["epoch"], "%Y-%m-%dT%H:%M:00.000Z"))
	cfg.delegate = constants["activeDelegates"]

	cfg.headers["nethash"] = data["nethash"]
	# cfg.headers["version"] = data["version"]
	cfg.fees = constants["dynamicOffsets"]
	cfg.explorer = data["explorer"]
	cfg.token = data["token"]
	cfg.symbol = data["symbol"]
	cfg.ports = data["ports"]

	crypto.getBytes = getBytes

	select_peers()
	DAEMON_PEERS = rotate_peers()


def stop():
	global DAEMON_PEERS
	Transaction.DFEES = False
	crypto.getBytes = _getBytes
	DAEMON_PEERS.set()
