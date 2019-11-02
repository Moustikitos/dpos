# -*- coding: utf-8 -*-
# © Toons
import binascii
import hashlib
import base58

from ecpy.curves import Curve, Point
from ecpy.keys import ECPublicKey, ECPrivateKey
from ecpy.ecdsa import ECDSA
from ecpy.ecschnorr import ECSchnorr

from dposlib import BytesIO
from dposlib.blockchain import cfg
from dposlib.util.bin import hexlify, unhexlify, pack, pack_bytes

SECP256K1 = Curve.get_curve("secp256k1")


def ecPublicKey2Hex(ecpublickey):
	"""
	Convert an ecpy.keys.ECPublicKey to a hex string.

	Argument:
	ecpublickey (ecpy.keys.ECPublicKey) -- an ecpy.keys.ECPublicKey instance

	Returns str
	"""	
	return hexlify(ecpublickey.W.to_bytes(compressed=True))


def hex2EcPublicKey(pubkey):
	"""
	Convert a valid hex string public key to an ecpy.keys.ECPublicKey.

	Argument:
	pubkey (str) -- a valid hex string public key

	Returns ecpy.keys.ECPublicKey
	"""	
	return ECPublicKey(Point.from_bytes(unhexlify(pubkey), SECP256K1))


def getKeys(secret, seed=None):
	"""
	Generate keyring containing public key, signing and checking keys as
	attribute.

	Arguments:
	secret (str or bytes) -- a human pass phrase
	Keyword argument:
	seed (byte) -- a sha256 sequence bytes (private key actualy)

	Return dict
	"""
	if secret and not isinstance(secret, bytes): secret = secret.encode('utf-8')
	seed = hashlib.sha256(secret).digest() if not seed else seed
	hex_seed = hexlify(seed)
	privateKey = ECPrivateKey(int(hex_seed, 16), SECP256K1)
	publicKey = privateKey.get_public_key()

	return {
		"publicKey": ecPublicKey2Hex(publicKey),
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
	Computes ARK address from publicKey.

	Argument:
	publicKey (str) -- public key string
	Keyword argument:
	marker (int) -- network marker (optional)

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
	return str(b58.decode('utf-8') if isinstance(b58, bytes) else b58)


def wifSignature(tx, wif):
	return wifSignatureFromBytes(getBytes(tx), wif)


def wifSignatureFromBytes(data, wif):
	seed = base58.b58decode_check(wif)[1:33]
	return getSignatureFromBytes(data, hexlify(seed))


def getSignature(tx, privateKey):
	"""
	Generate transaction signature using private key.

	Arguments:
	tx (dict) -- a transaction description
	privateKey (str) -- a private key as hex string

	Return str
	"""
	return getSignatureFromBytes(getBytes(tx), privateKey)


def getSignatureFromBytes(data, privateKey):
	"""
	Generate data signature using private key.

	Arguments:
	data (bytes) -- data in bytes
	privateKey (str) -- a private key as hex string
	Keyword argument:
	schnorr (boolean) -- a flag to use schnorr signature

	Return str
	"""
	privateKey = ECPrivateKey(int(privateKey, 16), SECP256K1)
	message = hashlib.sha256(data).digest()
	if bytearray(data)[0] == 0xff:
		signer = ECSchnorr(hashlib.sha256, fmt="RAW")
		return hexlify(signer.bcrypto410_sign(message, privateKey))
		# return hexlify(signer.bip_sign(message, privateKey))
	else:
		signer = ECDSA("DER")
		return hexlify(signer.sign_rfc6979(message, privateKey, hashlib.sha256, canonical=True))


def checkTransaction(tx, secondPublicKey=None):
	"""
	Verify transaction validity.

	Arguments:
	tx (dict) -- transaction object
	Keyword argument:
	secondPublicKey (str) -- secondPublicKey to use

	Return bool
	"""
	checks = []
	version = tx.get("version", 0x01)
	publicKey = tx["senderPublicKey"]
	# pure python dict serializer
	_ser = lambda t,v: serialize(t, version=v) if v >= 0x02 else getBytes(t)
	# create a local copy of tx
	tx = dict(**tx)
	# id check
	# remove id from tx if any and then compare
	id_ = tx.pop("id", False)
	if id_:
		checks.append([getIdFromBytes(_ser(tx, version)) == id_])
	# signatures check
	# remove all signatures from tx and then check first signature if any
	signature = tx.pop("signature", False)
	signSignature = tx.pop("signSignature", tx.pop("secondSignature", False))
	if signature:
		checks.append(verifySignatureFromBytes(
			_ser(tx, version),
			publicKey,
			signature
		))
	# add signature and then check second signature if any
	tx["signature"] = signature
	if signSignature and secondPublicKey:
		checks.append(verifySignatureFromBytes(
			_ser(tx, version),
			secondPublicKey,
			signSignature
		))
	return not False in checks


def verifySignature(value, publicKey, signature):
	"""
	Verify signature.

	Arguments:
	value (str) -- value as hex string
	publicKey (str) -- a public key as hex string
	signature (str) -- a signature as hex string
	Keyword argument:
	schnorr (boolean) -- a flag to use schnorr verification

	Return bool
	"""
	return verifySignatureFromBytes(unhexlify(value), publicKey, signature)


def verifySignatureFromBytes(data, publicKey, signature):
	"""
	Verify signature.

	Arguments:
	data (bytes) -- data in bytes
	publicKey (str) -- a public key as hex string
	signature (str) -- a signature as hex string
	Keyword argument:
	schnorr (boolean) -- a flag to use schnorr verification

	Return bool
	"""
	publicKey = hex2EcPublicKey(publicKey)
	message = hashlib.sha256(data).digest()
	if len(signature) == 128:
		verifier = ECSchnorr(hashlib.sha256, fmt="RAW")
		return verifier.bcrypto410_verify(message, unhexlify(signature), publicKey)
		# return verifier.bip_verify(message, unhexlify(signature), publicKey)
	else:
		verifier = ECDSA("DER")
		return verifier.verify(message, unhexlify(signature), publicKey)


def getId(tx):
	"""
	Generate transaction id.

	Argument:
	tx (dict) -- a transaction description

	Return str
	"""
	return getIdFromBytes(getBytes(tx, exclude_multi_sig=False))


def getIdFromBytes(data):
	"""
	Generate data id.

	Argument:
	data (bytes) -- data in bytes

	Return str
	"""
	return hexlify(hashlib.sha256(data).digest())


def getBytes(tx, exclude_multi_sig=True):
	"""
	Hash transaction object into bytes data.

	Argument:
	tx (dict) -- transaction object

	Return bytes sequence
	"""
	if tx.get("version", 0x01) >= 0x02:
		return serialize(tx, exclude_multi_sig=exclude_multi_sig)

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
	# deal with vendorField values
	if "vendorFieldHex" in tx:
		vendorField = unhexlify(tx["vendorFieldHex"])
	else:
		value = tx.get("vendorField", b"")
		if not isinstance(value, bytes):
			value = value.encode("utf-8")
		vendorField = value
	vendorField = vendorField[:64].ljust(64, b"\x00")
	pack_bytes(buf, vendorField)
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
	elif tx.get("secondSignature", False):
		pack_bytes(buf, unhexlify(tx["secondSignature"]))

	result = buf.getvalue()
	buf.close()
	return result


# Reference: 
# - https://github.com/ArkEcosystem/AIPs/blob/master/AIPS/aip-11.md
# - https://github.com/ArkEcosystem/AIPs/blob/master/AIPS/aip-102.md
def serialize(tx, version=None, exclude_multi_sig=True):
	"""
	Serialize transaction object.

	Argument:
	tx (dict) -- transaction object

	Return bytes sequence
	"""
	buf = BytesIO()
	version = tx.get("version", 0x01) if not version else version

	# deal with vendorField
	if "vendorFieldHex" in tx:
		vendorField = unhexlify(tx["vendorFieldHex"])
	else:
		vendorField = tx.get("vendorField", "")
		if not isinstance(vendorField, bytes):
			vendorField = vendorField.encode("utf-8")
	vendorField = vendorField[:255] # "vendorFieldLength" = 255 since height 8,128,000

	# common part
	pack("<BBB", buf, (0xff, version, cfg.pubKeyHash))
	if version >= 0x02:
		pack("<IHQ", buf, (tx.get("typeGroup", 1), tx["type"], tx["nonce"],))
	else:
		pack("<BI", buf, (tx["type"], tx["timestamp"],))
	pack_bytes(buf, unhexlify(tx["senderPublicKey"]))
	pack("<QB", buf, (tx["fee"], len(vendorField)))
	pack_bytes(buf, vendorField)

	# custom part
	pack_bytes(buf, serializePayload(tx))

	# signatures part
	if "signature" in tx:
		pack_bytes(buf, unhexlify(tx["signature"]))
	if "signSignature" in tx:
		pack_bytes(buf, unhexlify(tx["signSignature"]))
	elif "secondSignature" in tx:
		pack_bytes(buf, unhexlify(tx["secondSignature"]))

	if "signatures" in tx and not exclude_multi_sig:
		if version == 0x01:
			pack("<B", buf, (0xff,))
		pack_bytes(buf, b"".join([unhexlify(sig) for sig in tx["signatures"]]))

	# id part
	if "id" in tx:
		pack_bytes(buf, unhexlify(tx["id"]))

	result = buf.getvalue()
	buf.close()
	return result


def serializePayload(tx):
	asset = tx.get("asset", {})
	buf = BytesIO()
	_type = tx["type"]

	# transfer transaction
	if _type == 0:
		try:
			recipientId = base58.b58decode_check(tx["recipientId"])
		except:
			raise Exception("no recipientId defined")
		pack("<QI", buf, (
			int(tx.get("amount", 0)),
			int(tx.get("expiration", 0)),
		))
		pack_bytes(buf, recipientId)

	# secondSignature registration
	elif _type == 1:
		if "signature" in asset:
			secondPublicKey = asset["signature"]["publicKey"]
		else:
			raise Exception("no secondSecret or secondPublicKey given")
		pack_bytes(buf, unhexlify(secondPublicKey))

	# delegate registration
	elif _type == 2:
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
	elif _type == 3:
		delegatePublicKeys = asset.get("votes", False)
		if delegatePublicKeys:
			pack("<B", buf, (len(delegatePublicKeys), ))
			for delegatePublicKey in delegatePublicKeys:
				delegatePublicKey = delegatePublicKey.replace("+", "01").replace("-", "00")
				pack_bytes(buf, unhexlify(delegatePublicKey))
		else:
			raise Exception("no up/down vote given")

	# Multisignature registration
	elif _type == 4:
		multiSignature = asset.get("multiSignature", False)
		if multiSignature:
			pack("<BB", buf, (multiSignature["min"], len(multiSignature["publicKeys"])))
			pack_bytes(buf, b"".join([unhexlify(sig) for sig in multiSignature["publicKeys"]]))

	# IPFS
	elif _type == 5:
		try:
			data = base58.b58decode(asset["ipfs"])
		except:
			raise Exception("bad ipfs autentification")
		pack_bytes(buf, data)

	# multipayment
	elif _type == 6:
		try:
			items = [(p["amount"], base58.b58decode_check(p["recipientId"])) for p in asset.get("payments", {})]
		except:
			raise Exception("error in recipientId address list")
		result = pack("<I", buf, (len(items), ))
		for amount,address in items:
			pack("<Q", buf, (amount, ))
			pack_bytes(buf, address)

	# delegate resignation
	elif _type == 7:
		pass

	# HTLC lock
	elif _type == 8:
		try:
			recipientId = base58.b58decode_check(tx["recipientId"])
		except:
			raise Exception("no recipientId defined")
		lock = asset.get("lock", False)
		expiration = lock.get("expiration", False)
		if not lock or not expiration:
			raise Exception("no lock nor expiration data found")
		pack("<Q", buf, (int(tx.get("amount", 0)),))
		pack_bytes(buf, unhexlify(lock["secretHash"]))
		pack("<BI", buf, [int(expiration["type"]), int(expiration["value"])]) 
		pack_bytes(buf, recipientId)

	# HTLC claim
	elif _type == 9:
		claim = asset.get("claim", False)
		if not claim:
			raise Exception("no claim data found")
		pack_bytes(buf, unhexlify(claim["lockTransactionId"]))
		pack_bytes(buf, claim["unlockSecret"].encode("utf-8"))

	# HTLC refund
	elif _type == 10:
		refund = asset.get("refund", False)
		if not refund:
			raise Exception("no refund data found")
		pack_bytes(buf, unhexlify(refund["lockTransactionId"]))

	else:
		raise Exception("Unknown transaction type %d" % tx["type"])

	result = buf.getvalue()
	buf.close()
	return result


# ~ https://blockstream.com/2018/01/23/en-musig-key-aggregation-schnorr-signatures/
####
# Schnorr signatures
# As a refresher, here are the equations relevant for Schnorr signatures:

# Signatures are (R,s) = (rG, r + H(X,rG,m)x) where r is a random nonce chosen by the signer
# Verification requires sG = R + H(X,R,m)X

####
# Naive Schnorr multi-signatures (! rogue-key attack !)
# A straightforward generalization is possible to support multi-signatures:

# Call X the sum of the Xi points
# Each signer chooses a random nonce ri, and shares Ri = riG with the other signers
# Call R the sum of the Ri points
# Each signer computes si = ri + H(X,R,m)xi
# The final signature is (R,s) where s is the sum of the si values
# Verification requires sG = R + H(X,R,m)X, where X is the sum of the individual public keys

####
# Bellare-Neven
# As mentioned above, the BN multi-signature scheme is secure without such assumptions. Here is how it works:

# Call L = H(X1,X2,…)
# Each signer chooses a random nonce ri, and shares Ri = riG with the other signers
# Call R the sum of the Ri points
# Each signer computes si = ri + H(L,Xi,R,m)xi
# The final signature is (R,s) where s is the sum of the si values
# Verification requires sG = R + H(L,X1,R,m)X1 + H(L,X2,R,m)X2 + …

####
# MuSig
# This is where MuSig comes in. It recovers the key aggregation property without losing security:

# Call L = H(X1,X2,…) (hash all publicKey together)
# Call X the sum of all H(L,Xi)Xi
# Each signer chooses a random nonce ri, and shares Ri = riG with the other signers
# Call R the sum of the Ri points
# Each signer computes si = ri + H(X,R,m)H(L,Xi)xi
# The final signature is (R,s) where s is the sum of the si values
# Verification again satisfies sG = R + H(X,R,m)X
