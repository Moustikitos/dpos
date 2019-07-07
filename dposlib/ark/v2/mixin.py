# -*- coding: utf-8 -*-
# © Toons

import os
import struct
import datetime
from collections import OrderedDict

import pytz
from dposlib import rest, BytesIO
from dposlib.ark import crypto
from dposlib.blockchain import Transaction, slots, cfg
from dposlib.util.bin import pack, pack_bytes, unhexlify, hexlify


class DataIterator:

	def __init__(self, endpoint, tries=10):
		if not isinstance(endpoint, rest.EndPoint):
			raise Exception("Invalid endpoint class")
		self.endpoint = endpoint
		self.data = {}
		self.page = 0
		self.errors = 0
		self.tries = tries

	def __next__(self):
		if not self.data.get("meta", {}).get("next", None) and self.page:
			raise StopIteration("End of data reached")
		else:
			self.data = self.endpoint(page=self.page+1)
			if self.data.get("error", False):
				self.errors += 1
			else:
				self.page += 1
		return self.data.get("data", [])
	next = __next__

	def __iter__(self):
		while True:
			try:
				yield next(self)
			except:
				break
			else:
				if self.errors > self.tries:
					raise Exception("Too much unsuccesfull tries")


def serializePayload(tx):
	asset = tx.get("asset", {})
	buf = BytesIO()

	# transfer transaction
	if tx["type"] == 0:
		try:
			recipientId = crypto.base58.b58decode_check(tx["recipientId"])
		except:
			raise Exception("no recipientId defined")
		pack("<QI", buf, (
			int(tx.get("amount", 0)),
			int(tx.get("expiration", 0)),
		))
		pack_bytes(buf, recipientId)
	# secondSignature registration
	elif tx["type"] == 1:
		if "signature" in asset:
			secondPublicKey = asset["signature"]["publicKey"]
		else:
			raise Exception("no secondSecret or secondPublicKey given")
		pack_bytes(buf, unhexlify(secondPublicKey))
	# delegate registration
	elif tx["type"] == 2:
		username = asset.get("delegate", {}).get("username", False)
		if username:
			length = len(username)
			if 3 <= length <= 255:
				pack("<B", buf, (length, ))
				pack_bytes(buf, username.encode("utf-8"))
			else:
				raise Exception("bad username length [3-255]: %s" % username)
		else:
			raise Exception("no username defined")
	# vote
	elif tx["type"] == 3:
		delegatePublicKeys = asset.get("votes", False)
		if delegatePublicKeys:
			payload = pack("<B", buf, (len(delegatePublicKeys), ))
			for delegatePublicKey in delegatePublicKeys:
				delegatePublicKey = delegatePublicKey.replace("+", "01").replace("-", "00")
				pack_bytes(buf, unhexlify(delegatePublicKey))
		else:
			raise Exception("no up/down vote given")
	# IPFS
	elif tx["type"] == 5:
		dag = asset.get("ipfs", {}).get("dag", False)
		if dag:
			dag = unhexlify(dag)
			pack("<B", buf, (len(dag), ))
			pack_bytes(buf, dag)
		else:
			raise Exception("no IPFS DAG given")
	# timelock transaction
	elif tx["type"] == 6:
		try:
			recipientId = crypto.base58.b58decode_check(tx["recipientId"])
		except:
			raise Exception("no recipientId defined")
		pack("<QBI", buf, (
			int(tx.get("amount", 0)),
			int(tx.get("timelockType", 0)),
			int(tx.get("timelock", 0)),
		))
		pack_bytes(buf, recipientId)
	# multipayment
	elif tx["type"] == 7:
		try:
			items = [(p["amount"], crypto.base58.b58decode_check(p["recipientId"])) for p in asset.get("payments", {})]
		except:
			raise Exception("error in recipientId address list")
		result = pack(buf, "<H", (len(items), ))
		for amount,address in items:
			pack("<Q", buf, (amount, ))
			pack_bytes(buf, address)
	# delegate resignation
	elif tx["type"] == 8:
		pass

	else:
		raise Exception("Unknown transaction type %d" % tx["type"])

	result = buf.getvalue()
	buf.close()
	return result


# Reference: https://github.com/ArkEcosystem/AIPs/blob/master/AIPS/aip-11.md
def serialize(tx):
	buf = BytesIO()

	# deal with vendorField
	if "vendorFieldHex" in tx:
		vendorField = unhexlify(tx["vendorFieldHex"])
	else:
		vendorField = tx.get("vendorField", "").encode("utf-8")

	# common part
	# pack("<BBBBI", buf, (255, Transaction.VERSION, rest.cfg.pubKeyHash, tx["type"], tx["timestamp"]))
	pack("<BBBI", buf, (Transaction.VERSION, rest.cfg.pubKeyHash, tx["type"], tx["timestamp"]))
	pack_bytes(buf, unhexlify(tx["senderPublicKey"]))
	pack("<QB", buf, (tx["fee"], len(vendorField)))
	pack_bytes(buf, vendorField)
	
	# custom part
	pack_bytes(buf, serializePayload(tx))
	
	# signatures part
	pack_bytes(buf, unhexlify(tx["signature"]))
	if "signSignature" in tx:
		pack_bytes(buf, unhexlify(tx["signSignature"]))
	elif "secondSignature" in tx:
		pack_bytes(buf, unhexlify(tx["secondSignature"]))

	# id part
	if "id" in tx:
		pack_bytes(buf, unhexlify(tx["id"]))

	result = buf.getvalue()
	buf.close()
	return result


def loadPages(endpoint, pages=False, nb_tries=10, limit=False, **kx):
	data_iterator = DataIterator(endpoint, nb_tries)
	data = []
	while True:
		try:
			if limit and len(data) > limit:
				break
			_data = next(data_iterator)
		except StopIteration:
			break
		else:
			if not pages or data_iterator.page <= pages:
				data.extend(_data)
			else:
				break
				
	if limit:
		return data[:limit]
	else:
		return data


def deltas():
	delegates = loadPages(rest.GET.api.delegates)
	blocks = [d["blocks"] for d in delegates]
	produced = sum(b["produced"] for b in blocks)

	last_block_timestamp = slots.getRealTime(delegates[0]["blocks"]["last"]["timestamp"]["epoch"])
	total_elapsed_time = (last_block_timestamp - rest.cfg.begintime).total_seconds()

	theorical_height = int((datetime.datetime.now(pytz.UTC) - rest.cfg.begintime).total_seconds() / rest.cfg.blocktime)

	return OrderedDict({
		"real blocktime": total_elapsed_time / produced,
		"block produced (real height)": produced,
		"theorical height": theorical_height,
		"height shift": produced - theorical_height,
	})
