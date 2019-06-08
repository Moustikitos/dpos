# -*- coding: utf-8 -*-
# © Toons

import hashlib
import struct

from dposlib.blockchain import cfg
from dposlib.util.bin import hexlify, pack, pack_bytes, unhexlify

from nacl.bindings import crypto_sign_BYTES
from nacl.bindings.crypto_sign import crypto_sign, crypto_sign_seed_keypair

from dposlib import BytesIO


def getKeys(secret, seed=None):
	if not isinstance(secret, bytes): secret = secret.encode('utf-8')
	seed = hashlib.sha256(secret).digest() if not seed else seed
	publicKey, privateKey = list(hexlify(e) for e in crypto_sign_seed_keypair(seed))
	return {"publicKey": publicKey, "privateKey": privateKey}


def getAddress(public):
	seed = hashlib.sha256(unhexlify(public)).digest()
	return "%s%s" % (struct.unpack("<Q", seed[:8]) + (cfg.marker,))


def getSignature(tx, private):
	return hexlify(
		crypto_sign(
			hashlib.sha256(getBytes(tx)).digest(),
			unhexlify(private)
		)[:crypto_sign_BYTES]
	)


def getId(tx):
	seed = hashlib.sha256(getBytes(tx)).digest()
	return "%s" % struct.unpack("<Q", seed[:8])


def getBytes(tx):
	buf = BytesIO()

	# write type and timestamp
	pack("<bi", buf, (tx["type"], tx["timestamp"]))
	# write senderPublicKey as bytes in buffer
	pack_bytes(buf, unhexlify(tx["senderPublicKey"]))
	# if there is a requesterPublicKey
	if "requesterPublicKey" in tx:
		pack_bytes(buf, unhexlify(tx["requesterPublicKey"]))
	# if there is a recipientId
	if "recipientId" in tx:
		pack(">Q", buf, (int(tx["recipientId"][:-len(cfg.marker)]),))
	else:
		pack(">Q", buf, (0,))
	# write amount
	pack("<Q", buf, (int(tx["amount"]),))
	# if there is asset data
	if tx.get("asset", False):
		asset = tx["asset"]
		typ = tx["type"]
		if typ == 1 and "signature" in asset:
			pack_bytes(buf, unhexlify(asset["signature"]["publicKey"]))
		elif typ == 2 and "delegate" in asset:
			pack_bytes(buf, asset["delegate"]["username"].encode("utf-8"))
		elif typ == 3 and "votes" in asset:
			pack_bytes(buf, "".join(asset["votes"]).encode("utf-8"))
		else:
			pass
	# if there is a signature
	if tx.get("signature", False):
		pack_bytes(buf, unhexlify(tx["signature"]))
	# if there is a second signature
	if tx.get("signSignature", False):
		pack_bytes(buf, unhexlify(tx["signSignature"]))

	result = buf.getvalue()
	buf.close()
	return result
