# -*- coding: utf-8 -*-
# © Toons

import base58
import hashlib
import pySecp256k1 as secp256k1

from pySecp256k1 import schnorr, ecdsa
from dposlib import BytesIO, PY3
from dposlib.blockchain import cfg
from dposlib.blockchain.tx import serialize
from dposlib.util.bin import hexlify, unhexlify, pack, pack_bytes

if PY3:
    unicode = str


def getKeys(secret):
    """
    Generate keyring containing secp256k1 keys-pair and wallet import format
    (WIF).

    Args:
        secret (str, bytes or int): anything that could issue a private key on
                                    secp256k1 curve
    Returns:
        public, private and WIF keys
    """
    if isinstance(secret, (str, bytes, unicode)):
        try:
            seed = unhexlify(secret)
        except Exception:
            seed = secp256k1.hash_sha256(secret)
    else:
        seed = secp256k1.bytes_from_int(secret)
    publicKey = secp256k1.PublicKey.from_seed(seed)
    return {
        "publicKey": hexlify(publicKey.encode()),
        "privateKey": hexlify(seed),
        "wif": getWIF(seed)
    }


def getMultiSignaturePublicKey(minimum, *publicKeys):
    """
    Compute ARK multi signature public key according to [ARK AIP #18](
        https://github.com/ArkEcosystem/AIPs/blob/master/AIPS/aip-18.md
    ).

    Args:
        minimum (int): minimum signature required
        publicKeys (list of str): public key list
    Returns:
        the multisignature public key
    """
    if 2 > minimum > len(publicKeys):
        raise ValueError("min signatures value error")
    P = secp256k1.PublicKey.from_secret("%02x" % minimum)
    for publicKey in publicKeys:
        P = P + secp256k1.PublicKey.decode(unhexlify(publicKey))
    return hexlify(P.encode())


def getAddressFromSecret(secret, marker=None):
    """
    Compute ARK address from secret.

    Args:
        secret (str): secret string
        marker (int): network marker (optional)
    Returns:
        the address
    """
    return getAddress(getKeys(secret)["publicKey"], marker)


def getAddress(publicKey, marker=None):
    """
    Compute ARK address from publicKey.

    Args:
        publicKey (str): public key
        marker (int): network marker (optional)
    Returns:
        the address
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
    Compute WIF address from seed.

    Args:
        seed (bytes): a sha256 sequence bytes
    Returns:
        WIF address
    """
    if hasattr(cfg, "wif"):
        seed = unhexlify(cfg.wif) + seed[:32] + b"\x01"  # \x01 -> compressed
        b58 = base58.b58encode_check(seed)
        return str(b58.decode('utf-8') if isinstance(b58, bytes) else b58)


def wifSignature(tx, wif):
    """
    Generate transaction signature using private key.

    Args:
        tx (dict or Transaction): transaction description
        wif (str): wif key
    Returns:
        signature
    """
    return wifSignatureFromBytes(getBytes(tx), wif)


def wifSignatureFromBytes(data, wif):
    """
    Generate signature from data using WIF key.

    Args:
        data (bytes): bytes sequence
        wif (str): wif key
    Returns:
        signature
    """
    seed = base58.b58decode_check(
        str(wif) if not isinstance(wif, bytes) else wif
    )[1:33]
    return getSignatureFromBytes(data, hexlify(seed))


def getSignature(tx, privateKey, **options):
    """
    Generate transaction signature using private key.

    Args:
        tx (dict or Transaction): transaction description
        privateKey (str): private key as hex string
    Keyword args:
        exclude_sig (bool):
            exclude signature during tx serialization [defalut: True]
        exclude_multi_sig(bool):
            exclude signatures during tx serialization [defalut: True]
        exclude_second_sig(bool):
            exclude second signatures during tx serialization [defalut: True]
    Returns:
        signature
    """
    return getSignatureFromBytes(getBytes(tx, **options), privateKey)


def getSignatureFromBytes(data, privateKey):
    """
    Generate signature from data using private key.

    Args:
        data (bytes): bytes sequence
        privateKey (str): private key as hex string
    Returns:
        signature as hex string
    """
    secret0 = unhexlify(privateKey)
    msg = secp256k1.hash_sha256(data)
    if bytearray(data)[0] == 0xff:
        return hexlify(schnorr.bcrypto410_sign(msg, secret0))
    else:
        return hexlify(ecdsa.rfc6979_sign(msg, secret0, canonical=True))


def verifySignature(value, publicKey, signature):
    """
    Verify signature.

    Args:
        value (str): value as hex string
        publicKey (str): public key as hex string
        signature (str): signature as hex string
    Returns:
        True if signature matches the public key
    """
    return verifySignatureFromBytes(unhexlify(value), publicKey, signature)


def verifySignatureFromBytes(data, publicKey, signature):
    """
    Verify signature.

    Args:
        data (bytes): data
        publicKey (str): public key as hex string
        signature (str): signature as hex string
    Returns:
        True if signature matches the public key
    """
    pubkey = unhexlify(publicKey)
    msg = secp256k1.hash_sha256(data)
    sig = unhexlify(signature)
    if len(signature) == 128:
        return schnorr.bcrypto410_verify(msg, pubkey, sig)
    else:
        return ecdsa.verify(msg, pubkey, sig)


def getId(tx):
    """
    Generate transaction id.

    Args:
        tx (dict or Transaction): transaction object
    Returns:
        id as hex string
    """
    return getIdFromBytes(getBytes(tx, exclude_multi_sig=False))


def getIdFromBytes(data):
    """
    Generate data id.

    Args:
        data (bytes): data as bytes sequence
    Returns:
        id as hex string
    """
    return hexlify(secp256k1.hash_sha256(data))


# TO BE DEPRECATED WITH ARK CORE 3.0
def getBytes(tx, **options):
    """
    Hash transaction.

    Args:
        tx (dict or Transaction): transaction object
    Keyword args:
        exclude_sig (bool):
            exclude signature during tx serialization [defalut: True]
        exclude_multi_sig(bool):
            exclude signatures during tx serialization [defalut: True]
        exclude_second_sig(bool):
            exclude second signatures during tx serialization [defalut: True]
    Returns:
        bytes sequence
    """
    if tx.get("version", 0x01) >= 0x02:
        return serialize(tx, **options)

    buf = BytesIO()
    # write type and timestamp
    pack("<BI", buf, (tx["type"], int(tx["timestamp"])))
    # write senderPublicKey as bytes in buffer
    if "senderPublicKey" in tx:
        pack_bytes(buf, unhexlify(tx["senderPublicKey"]))
    # if there is a requesterPublicKey
    if "requesterPublicKey" in tx:
        pack_bytes(buf, unhexlify(tx["requesterPublicKey"]))
    # if there is a recipientId or tx not a second secret nor a multi
    # singature registration
    if tx.get("recipientId", False) and tx["type"] not in [1, 4]:
        recipientId = tx["recipientId"]
        recipientId = base58.b58decode_check(
            str(recipientId) if not isinstance(recipientId, bytes) else
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
    if "signature" in tx and not options.get("exclude_sig", False):
        pack_bytes(buf, unhexlify(tx["signature"]))
    # if there is a second signature
    if not options.get("exclude_second_sig", False):
        if tx.get("signSignature", False):
            pack_bytes(buf, unhexlify(tx["signSignature"]))
        elif tx.get("secondSignature", False):
            pack_bytes(buf, unhexlify(tx["secondSignature"]))

    result = buf.getvalue()
    buf.close()
    return result


def checkTransaction(tx, secondPublicKey=None, multiPublicKeys=[]):
    """
    Verify transaction validity.

    Args:
        tx (dict or Transaction):
            transaction object
        secondPublicKey (str):
            second public key to use if needed
        multiPublicKeys (list):
            owners public keys (sorted according to associated type-4-tx asset)
    Returns:
        True if transaction is valid
    """
    checks = []
    version = tx.get("version", 0x01)
    publicKey = tx["senderPublicKey"]

    if tx["type"] == 4:
        multiPublicKeys = tx["asset"]["multiSignature"]["publicKeys"]

    # pure python dict serializer
    def _ser(t, v, **opt):
        return \
            serialize(t, version=v, **opt) if v >= 0x02 else \
            getBytes(t, **opt)

    # create a local copy of tx
    tx = dict(**tx)

    # id check
    # remove id from tx if any and then compare
    id_ = tx.pop("id", False)
    if id_:
        checks.append(getIdFromBytes(_ser(tx, version)) == id_)

    signature = tx.pop("signature", False)
    signSignature = tx.pop("signSignature", tx.pop("secondSignature", False))
    signatures = tx.pop("signatures", [])

    # multiple signature check
    if len(multiPublicKeys) and len(signatures):
        serialized = _ser(tx, version)
        for sig in signatures:
            idx, sig = int(sig[0:2], 16), sig[2:]
            checks.append(verifySignatureFromBytes(
                serialized, multiPublicKeys[idx], sig
            ))
        tx["signatures"] = signatures

    if signature:
        # sender signature check
        checks.append(verifySignatureFromBytes(
            _ser(tx, version), publicKey, signature
        ))
        # sender second signature check
        if signSignature and secondPublicKey:
            # add signature before check
            tx["signature"] = signature
            checks.append(verifySignatureFromBytes(
                _ser(tx, version), secondPublicKey, signSignature
            ))

    return False not in checks
