# -*- coding: utf-8 -*-
# © Toons
import binascii
import hashlib
import base58

import ecpy.ecrand
from ecpy.curves import Curve, Point
from ecpy.keys import ECPublicKey, ECPrivateKey
from ecpy.ecdsa import ECDSA
from ecpy.ecschnorr import ECSchnorr
###
# here is a fix because rfc 6979 not implemented yet in ecpy.ecschnorr
# https://tools.ietf.org/html/rfc6979
def sign_rfc6979(cls, msg, pv_key, hasher, canonical=False):
	""" Signs a message hash  according to  RFC6979 
	Args:
		msg (bytes)                    : the message hash to sign
		pv_key (ecpy.keys.ECPrivateKey): key to use for signing
		hasher (hashlib)               : hasher conform to hashlib interface
	"""
	field = pv_key.curve.field
	V = None
	for i in range(1, cls.maxtries):
		k,V = ecpy.ecrand.rnd_rfc6979(msg, pv_key.d, field, hasher, V)
		sig = cls._do_sign(msg, pv_key, k)
		if sig:
			return sig
		return None
ECSchnorr.sign_rfc6979 = sign_rfc6979
###
from dposlib import BytesIO
from dposlib.blockchain import cfg
from dposlib.util.bin import basint, hexlify, pack, pack_bytes, unhexlify


def compressECPublicKey(ecpublickey):
	first, last = unhexlify("%x" % ecpublickey.W.x), unhexlify("%x" % ecpublickey.W.y)
	# check if last digit of second part is even (2%2 = 0, 3%2 = 1)
	even = not bool(basint(last[-1]) % 2)
	return (b"\x02" if even else b"\x03") + first


def uncompressECPublicKey(pubkey):
	"""
	Uncompressed public key is:
	0x04 + x-coordinate + y-coordinate

	Compressed public key is:
	0x02 + x-coordinate if y is even
	0x03 + x-coordinate if y is odd

	y^2 mod p = (x^3 + 7) mod p

	read more : https://bitcointalk.org/index.php?topic=644919.msg7205689#msg7205689
	"""
	p = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
	y_parity = int(pubkey[:2]) - 2
	x = int(pubkey[2:], 16)
	a = (pow(x, 3, p) + 7) % p
	y = pow(a, (p + 1) // 4, p)
	if y % 2 != y_parity:
		y = -y % p
	# return result as ECPublicKey
	return ECPublicKey(Point(x, y, Curve.get_curve("secp256k1"), check=True))


def getKeys(secret, seed=None):
	"""
	Generate keyring containing public key, signing and checking keys as
	attribute.

	Keyword arguments:
	secret (str or bytes) -- a human pass phrase
	seed (byte) -- a sha256 sequence bytes (private key actualy)

	Return dict
	"""
	if secret and not isinstance(secret, bytes): secret = secret.encode('utf-8')
	seed = hashlib.sha256(secret).digest() if not seed else seed
	hex_seed = hexlify(seed)
	privateKey = ECPrivateKey(int(hex_seed, 16), Curve.get_curve("secp256k1"))
	publicKey = privateKey.get_public_key()

	return {
		"publicKey": hexlify(compressECPublicKey(publicKey)),
		"privateKey": hex_seed,
		"wif": getWIF(seed)
	}


def getAddressFromSecret(secret):
	"""
	Computes ARK address from secret.

	Argument:
	secret (str) -- secret string

	Return str
	"""
	return getAddress(getKeys(secret)["publicKey"])


def getAddress(publicKey, marker=None):
	"""
	Computes ARK address from keyring.

	Argument:
	publicKey (str) -- public key string

	Return str
	"""
	if marker and isinstance(marker, int):
		marker = hex(marker)[2:]
	else:
		marker = None
	ripemd160 = hashlib.new('ripemd160', unhexlify(publicKey)).digest()[:20]
	seed = unhexlify(cfg.marker if not marker else marker) + ripemd160
	b58 = base58.b58encode_check(seed)
	return b58.decode('utf-8') if isinstance(b58, bytes) else b58


def getWIF(seed):
	"""
	Computes WIF address from seed.

	Argument:
	seed (bytes) -- a sha256 sequence bytes

	Return str
	"""
	seed = unhexlify(cfg.wif) + seed[:32] + (b"\x01" if cfg.compressed else b"")
	b58 = base58.b58encode_check(seed)
	return b58.decode('utf-8') if isinstance(b58, bytes) else b58


def getSignature(tx, privateKey, schnorr=False):
	"""
	Generate transaction signature using private key.

	Arguments:
	tx (dict) -- a transaction description
	privateKey (str) -- a private key as hex string

	Return str
	"""
	return getSignatureFromBytes(getBytes(tx), privateKey, schnorr)


def getSignatureFromBytes(data, privateKey, schnorr=False):
	"""
	Generate data signature using private key.

	Arguments:
	data (bytes) -- data in bytes
	privateKey (str) -- a private key as hex string

	Return str
	"""
	privateKey = ECPrivateKey(int(privateKey, 16), Curve.get_curve("secp256k1"))
	message = hashlib.sha256(data).digest()
	if schnorr:
		signer = ECSchnorr(hashlib.sha256, option="ISO", fmt="DER")
	else:
		signer = ECDSA("DER")
	return hexlify(signer.sign_rfc6979(message, privateKey, hashlib.sha256, canonical=True))


def verifySignature(value, publicKey, signature, schnorr=False):
	"""
	Verify signature.

	Arguments:
	value (bytes) -- value as hex string in bytes
	publicKey (str) -- a public key as hex string
	signature (str) -- a signature as hex string

	Return bool
	"""
	return verifySignatureFromBytes(unhexlify(value), publicKey, signature, schnorr)


def verifySignatureFromBytes(data, publicKey, signature, schnorr=False):
	"""
	Verify signature.

	Arguments:
	data (bytes) -- data in bytes
	publicKey (str) -- a public key as hex string
	signature (str) -- a signature as hex string

	Return bool
	"""
	publicKey = uncompressECPublicKey(publicKey)
	message = hashlib.sha256(data).digest()
	if schnorr:
		verifier = ECSchnorr(hashlib.sha256, option="ISO", fmt="DER")
	else:
		verifier = ECDSA("DER")
	return verifier.verify(message, unhexlify(signature), publicKey)


def getId(tx):
	"""
	Generate transaction id.

	Arguments:
	tx (dict) -- a transaction description

	Return str
	"""
	return getIdFromBytes(getBytes(tx))


def getIdFromBytes(data):
	"""
	Generate data id.

	Arguments:
	data (bytes) -- data in bytes

	Return str
	"""
	return hexlify(hashlib.sha256(data).digest())


def getBytes(tx):
	"""
	Hash transaction object into bytes data.

	Argument:
	tx (dict) -- transaction object

	Return bytes sequence
	"""
	if getattr(tx, "_version", 0x01) >= 0x02:
		return tx.serialize()

	buf = BytesIO()
	# write type and timestamp
	pack("<BI", buf, (tx["type"], int(tx["timestamp"])))
	# write senderPublicKey as bytes in buffer
	if "senderPublicKey" in tx:
		pack_bytes(buf, unhexlify(tx["senderPublicKey"]))
	# if there is a requesterPublicKey
	if "requesterPublicKey" in tx:
		pack_bytes(buf, unhexlify(tx["requesterPublicKey"]))
	# if there is a recipientId or tx not a second secret nor a multi singature registration
	if tx.get("recipientId", False) and tx["type"] not in [1, 4]:
		recipientId = tx["recipientId"]
		recipientId = base58.b58decode_check(
			str(recipientId) if not isinstance(recipientId, bytes) else \
			recipientId
		)
	else:
		recipientId = b"\x00" * 21
	pack_bytes(buf, recipientId)
	# if there is a vendorField
	if tx.get("vendorField", False):
		vendorField = tx["vendorField"][:64].ljust(64, "\x00")
	else:
		vendorField = "\x00" * 64
	pack_bytes(buf, vendorField.encode("utf-8"))
	# write amount and fee value
	pack("<QQ", buf, (tx.get("amount", 0), tx["fee"]))
	# if there is asset data
	if tx.get("asset", False):
		asset, typ = tx["asset"], tx["type"]
		if typ == 1 and "signature" in asset:
			pack_bytes(buf, unhexlify(asset["signature"]["publicKey"]))
		elif typ == 2 and "delegate" in asset:
			pack_bytes(buf, asset["delegate"]["username"].encode("utf-8"))
		elif typ == 3 and "votes" in asset:
			pack_bytes(buf, "".join(asset["votes"]).encode("utf-8"))
		else:
			raise Exception("transaction type %s not implemented" % typ)
	# if there is a signature
	if tx.get("signature", False):
		pack_bytes(buf, unhexlify(tx["signature"]))
	# if there is a second signature
	if tx.get("signSignature", False):
		pack_bytes(buf, unhexlify(tx["signSignature"]))

	result = buf.getvalue()
	buf.close()
	return result
