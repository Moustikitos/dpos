# -*- coding: utf-8 -*-
# © Toons
import binascii
import hashlib
import base58

from ecdsa import BadSignatureError
from ecdsa.der import UnexpectedDER
from ecdsa.curves import SECP256k1
from ecdsa.keys import SigningKey, VerifyingKey
from ecdsa.util import sigdecode_der, sigencode_der_canonize

from dposlib import BytesIO
from dposlib.blockchain import cfg
from dposlib.util.bin import basint, hexlify, pack, pack_bytes, unhexlify


def compressEcdsaPublicKey(pubkey):
	first, last = pubkey[:32], pubkey[32:]
	# check if last digit of second part is even (2%2 = 0, 3%2 = 1)
	even = not bool(basint(last[-1]) % 2)
	return (b"\x02" if even else b"\x03") + first


def uncompressEcdsaPublicKey(pubkey):
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
	# return result as der signature (no 0x04 preffix)
	return '{:x}{:x}'.format(x, y)


def getKeys(secret, seed=None):
	"""
	Generate keyring containing public key, signing and checking keys as
	attribute.

	Keyword arguments:
	secret (str or bytes) -- a human pass phrase
	seed (byte) -- a sha256 sequence bytes (private key actualy)

	Return dict
	"""
	if not isinstance(secret, bytes): secret = secret.encode('utf-8')
	seed = hashlib.sha256(secret).digest() if not seed else seed
	signingKey = SigningKey.from_secret_exponent(
		int(binascii.hexlify(seed), 16),
		SECP256k1,
		hashlib.sha256
	)
	publicKey = signingKey.get_verifying_key().to_string()
	return {
		"publicKey": hexlify(compressEcdsaPublicKey(publicKey) if cfg.compressed else publicKey),
		"privateKey": hexlify(signingKey.to_string()),
		"wif": getWIF(seed)
	}


def getAddress(publicKey):
	"""
	Computes ARK address from keyring.

	Argument:
	keys (ArkyDict) -- keyring returned by `getKeys`

	Return str
	"""
	ripemd160 = hashlib.new('ripemd160', unhexlify(publicKey)).digest()[:20]
	seed = unhexlify(cfg.marker) + ripemd160
	return base58.b58encode_check(seed)


def getWIF(seed):
	"""
	Computes WIF address from seed.

	Argument:
	seed (bytes) -- a sha256 sequence bytes

	Return str
	"""
	seed = unhexlify(cfg.wif) + seed[:32] + (b"\x01" if cfg.compressed else b"")
	return base58.b58encode_check(seed)


def getSignature(tx, privateKey):
	"""
	Generate transaction signature using private key.

	Arguments:
	tx (dict) -- a transaction description
	privateKey (str) -- a private key as hex string

	Return str
	"""
	signingKey = SigningKey.from_string(unhexlify(privateKey), SECP256k1, hashlib.sha256)
	return hexlify(signingKey.sign_deterministic(
		getBytes(tx),
		hashlib.sha256,
		sigencode=sigencode_der_canonize)
	)


def getSignatureFromBytes(data, privateKey):
	"""
	Generate data signature using private key.

	Arguments:
	data (bytes) -- data in bytes
	privateKey (str) -- a private key as hex string

	Return str
	"""
	signingKey = SigningKey.from_string(unhexlify(privateKey), SECP256k1, hashlib.sha256)
	return hexlify(signingKey.sign_deterministic(
		data,
		hashlib.sha256,
		sigencode=sigencode_der_canonize)
	)


def getId(tx):
	"""
	Generate transaction id.

	Arguments:
	tx (dict) -- a transaction description

	Return str
	"""
	return hexlify(hashlib.sha256(getBytes(tx)).digest())


def getIdFromBytes(data):
	"""
	Generate data id.

	Arguments:
	data (bytes) -- data in bytes

	Return str
	"""
	return hexlify(hashlib.sha256(data).digest())


def verifySignatureFromBytes(data, publicKey, signature):
	"""
	Verify signature.

	Arguments:
	data (bytes) -- data in bytes
	publicKey (str) -- a public key as hex string
	signature (str) -- a signature as hex string

	Return bool
	"""
	if len(publicKey) == 66:
		publicKey = uncompressEcdsaPublicKey(publicKey)
	verifyingKey = VerifyingKey.from_string(unhexlify(publicKey), SECP256k1, hashlib.sha256)
	try:
		verifyingKey.verify(unhexlify(signature), data, hashlib.sha256, sigdecode_der)
	except (BadSignatureError, UnexpectedDER):
		return False
	return True


def getBytes(tx):
	"""
	Hash transaction object into bytes data.

	Argument:
	tx (dict) -- transaction object

	Return bytes sequence
	"""
	buf = BytesIO()
	# write type and timestamp
	pack("<bi", buf, (tx["type"], int(tx["timestamp"])))
	# write senderPublicKey as bytes in buffer
	if "senderPublicKey" in tx:
		pack_bytes(buf, unhexlify(tx["senderPublicKey"]))
	# if there is a requesterPublicKey
	if "requesterPublicKey" in tx:
		pack_bytes(buf, unhexlify(tx["requesterPublicKey"]))
	# if there is a recipientId
	if tx.get("recipientId", False):
		recipientId = tx["recipientId"]
		recipientId = base58.b58decode_check(str(recipientId) if not isinstance(recipientId, bytes) \
			else recipientId)
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
	pack("<QQ", buf, (int(tx["amount"]), int(tx["fee"])))
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
