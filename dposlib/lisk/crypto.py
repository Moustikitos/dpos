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


	# function isSignatureTransaction () {
	# 	var bb = new ByteBuffer(32, true);
	# 	var publicKey = transaction.asset.signature.publicKey;
	# 	var publicKeyBuffer = Buffer.from(publicKey, 'hex');

	# 	for (var i = 0; i < publicKeyBuffer.length; i++) {
	# 		bb.writeByte(publicKeyBuffer[i]);
	# 	}

	# 	bb.flip();
	# 	var signatureBytes = new Uint8Array(bb.toArrayBuffer());

	# 	return {
	# 		assetBytes: signatureBytes,
	# 		assetSize: 32
	# 	};
	# }

	# /**
	#  * @method isDelegateTransaction
	#  * @return {object}
	#  */

	# function isDelegateTransaction () {
	# 	return {
	# 		assetBytes: Buffer.from(transaction.asset.delegate.username),
	# 		assetSize: Buffer.from(transaction.asset.delegate.username).length
	# 	};
	# }

	# /**
	#  * @method isVoteTransaction
	#  * @return {object}
	#  */

	# function isVoteTransaction () {
	# 	var voteTransactionBytes = (Buffer.from(transaction.asset.votes.join('')) || null);

	# 	return {
	# 		assetBytes: voteTransactionBytes,
	# 		assetSize: (voteTransactionBytes.length || 0)
	# 	};
	# }

	# /**
	#  * @method isMultisignatureTransaction
	#  * @return {object}
	#  */

	# function isMultisignatureTransaction () {
	# 	var MINSIGNATURES = 1;
	# 	var LIFETIME = 1;
	# 	var keysgroupBuffer = Buffer.from(transaction.asset.multisignature.keysgroup.join(''), 'utf8');

	# 	var bb = new ByteBuffer(MINSIGNATURES + LIFETIME + keysgroupBuffer.length, true);
	# 	bb.writeByte(transaction.asset.multisignature.min);
	# 	bb.writeByte(transaction.asset.multisignature.lifetime);
	# 	for (var i = 0; i < keysgroupBuffer.length; i++) {
	# 		bb.writeByte(keysgroupBuffer[i]);
	# 	}
	# 	bb.flip();

	# 	bb.toBuffer();
	# 	var multiSigBuffer = new Uint8Array(bb.toArrayBuffer());

	# 	return {
	# 		assetBytes: multiSigBuffer,
	# 		assetSize: multiSigBuffer.length
	# 	};
	# }

	# /**
	#  * @method isDappTransaction
	#  * @return {object}
	#  */

	# function isDappTransaction () {
	# 	var dapp = transaction.asset.dapp;
	# 	var buf = new Buffer([]);
	# 	var nameBuf = Buffer.from(dapp.name);
	# 	buf = Buffer.concat([buf, nameBuf]);

	# 	if (dapp.description) {
	# 		var descriptionBuf = Buffer.from(dapp.description);
	# 		buf = Buffer.concat([buf, descriptionBuf]);
	# 	}

	# 	if (dapp.tags) {
	# 		var tagsBuf = Buffer.from(dapp.tags);
	# 		buf = Buffer.concat([buf, tagsBuf]);
	# 	}

	# 	if (dapp.link) {
	# 		buf = Buffer.concat([buf, Buffer.from(dapp.link)]);
	# 	}

	# 	if (dapp.icon) {
	# 		buf = Buffer.concat([buf, Buffer.from(dapp.icon)]);
	# 	}

	# 	var bb = new ByteBuffer(4 + 4, true);
	# 	bb.writeInt(dapp.type);
	# 	bb.writeInt(dapp.category);
	# 	bb.flip();

	# 	buf = Buffer.concat([buf, bb.toBuffer()]);

	# 	return {
	# 		assetBytes: buf,
	# 		assetSize: buf.length
	# 	};
	# }

	# /**
	#  * @method isDappTransferTransaction
	#  * @return {object}
	#  */

	# function isDappTransferTransaction () {
	# 	var arrayBuf = new Buffer([]);
	# 	var dappBuffer = Buffer.from(transaction.asset.dapptransfer.dappid);
	# 	arrayBuf = Buffer.concat([arrayBuf, dappBuffer]);

	# 	return {
	# 		assetBytes: arrayBuf,
	# 		assetSize: arrayBuf.length
	# 	};
	# }

	# /**
	#  * @method isLockTransaction
	#  * @return {object}
	#  */

	# function isLockTransaction () {
	# 	var lock = transaction.asset.lock;

	# 	var byteBuf = new ByteBuffer(8, true);
	# 	byteBuf.writeUint64(lock.bytes, 0);
	# 	var arrayBuf = Buffer.from(new Uint8Array(byteBuf.toArrayBuffer()));

	# 	return {
	# 		assetBytes: arrayBuf,
	# 		assetSize: arrayBuf.length
	# 	};
	# }

	# /**
	#  * @method isPinTransaction
	#  * @return {object}
	#  */

	# function isPinTransaction () {
	# 	var pin = transaction.asset.pin;
	# 	var arrayBuf = new Buffer([]);

	# 	var hashBuf = Buffer.from(pin.hash.toString(), 'utf8');
	# 	arrayBuf = Buffer.concat([arrayBuf, hashBuf]);

	# 	var byteBuf = new ByteBuffer(8, true);
	# 	byteBuf.writeUint64(pin.bytes, 0);
	# 	byteBuf = Buffer.from(new Uint8Array(byteBuf.toArrayBuffer()));

	# 	arrayBuf = Buffer.concat([arrayBuf, byteBuf]);

	# 	if (pin.parent) {
	# 		var parentBuf = new ByteBuffer(8, true);
	# 		parentBuf.writeUint64(pin.parent, 0);
	# 		parentBuf = Buffer.from(new Uint8Array(parentBuf.toArrayBuffer()));

	# 		arrayBuf = Buffer.concat([arrayBuf, parentBuf]);
	# 	}

	# 	return {
	# 		assetBytes: arrayBuf,
	# 		assetSize: arrayBuf.length
	# 	};
	# }
