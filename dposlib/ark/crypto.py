# -*- coding: utf-8 -*-
# © Toons

import hashlib
import base58

from dposlib import BytesIO
from dposlib.ark import secp256k1
from dposlib.blockchain import cfg
from dposlib.util.bin import BHEX, hexlify, unhexlify, pack, pack_bytes
from dposlib.ark.secp256k1 import schnorr, ecdsa


def getKeys(secret):
    """
    Generate keyring containing secp256k1 keys-apir and wallet import format
    (WIF).

    Args:
        secret (:class:`str`, :class:`bytes` or :class:`int`):
            
    Returns:
        :class:`dict`: public, private and WIF keys
    """
    if isinstance(secret, str):
        seed = secp256k1.hash_sha256(secret)
    elif isinstance(bytes, str):
        seed = secret
    elif isinstance(secret, int):
        seed = secp256k1.bytes_from_int(secret)

    publicKey = secp256k1.PublicKey.from_seed(seed)
    return {
        "publicKey": hexlify(publicKey.encode()),
        "privateKey": hexlify(seed),
        "wif": getWIF(seed)
    }


def getAddressFromSecret(secret, marker=None):
    """
    Compute ARK address from secret.

    Args:
        secret (:class:`str`): secret string
        marker (:class:`int`): network marker (optional)

    Returns:
        :class:`str`: the address
    """
    return getAddress(getKeys(secret)["publicKey"], marker)


def getAddress(publicKey, marker=None):
    """
    Compute ARK address from publicKey.

    Args:
        publicKey (:class:`str`): public key
        marker (:class:`int`): network marker (optional)

    Returns:
        :class:`str`: the address
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
        seed (:class:`bytes`): a sha256 sequence bytes

    Returns:
        :class:`str`: WIF address
    """
    seed = unhexlify(cfg.wif) + seed[:32] + b"\x01"  # \x01 because compressed
    b58 = base58.b58encode_check(seed)
    return str(b58.decode('utf-8') if isinstance(b58, bytes) else b58)


def wifSignature(tx, wif):
    """
    Generate transaction signature using private key.

    Args:
        tx (:class:`dict` or :class:`Transaction`):
            transaction description
        wif (:class:`str`):
            wif key

    Returns:
        :class:`str`: signature
    """

    return wifSignatureFromBytes(getBytes(tx), wif)


def wifSignatureFromBytes(data, wif):
    """
    Generate signature from data using WIF key.

    Args:
        data (:class:`bytes`): bytes sequence
        wif (:class:`str`): wif key

    Returns:
        :class:`str`: signature
    """
    seed = base58.b58decode_check(
        str(wif) if not isinstance(wif, bytes) else wif
    )[1:33]
    return getSignatureFromBytes(data, hexlify(seed))


def getSignature(tx, privateKey):
    """
    Generate transaction signature using private key.

    Args:
        tx (:class:`dict` or :class:`Transaction`):
            transaction description
        privateKey (:class:`str`):
            private key as hex string

    Returns:
        :class:`str`: signature
    """
    return getSignatureFromBytes(getBytes(tx), privateKey)


def getSignatureFromBytes(data, privateKey):
    """
    Generate signature from data using private key.

    Args:
        data (:class:`bytes`): bytes sequence
        privateKey (:class:`str`): private key as hex string

    Returns:
        :class:`str`: signature as hex string
    """
    secret0 = unhexlify(privateKey)
    msg = secp256k1.hash_sha256(data)
    if bytearray(data)[0] == 0xff:
        return hexlify(schnorr.bcrypto410_sign(msg, secret0))
    else:
        return hexlify(ecdsa.rfc6979_sign(msg, secret0, canonical=True))


def checkTransaction(tx, secondPublicKey=None, multiPublicKeys=[]):
    """
    Verify transaction validity.

    Args:
        tx (:class:`dict` or :class:`Transaction`):
            transaction object
        secondPublicKey (:class:`str`):
            second public key to use if needed

    Returns:
        :class:`bool`: true if transaction is valid
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


def verifySignature(value, publicKey, signature):
    """
    Verify signature.

    Args:
        value (:class:`str`): value as hex string
        publicKey (:class:`str`): public key as hex string
        signature (:class:`str`): signature as hex string

    Returns:
        :class:`bool`: true if signature matches the public key
    """
    return verifySignatureFromBytes(unhexlify(value), publicKey, signature)


def verifySignatureFromBytes(data, publicKey, signature):
    """
    Verify signature.

    Args:
        data (:class:`bytes`): data
        publicKey (:class:`str`): public key as hex string
        signature (:class:`str`): signature as hex string

    Returns:
        :class:`bool`: true if signature matches the public key
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
        tx (:class:`dict` or :class:`Transaction`):
            transaction object

    Returns:
        :class:`str`: id as hex string
    """
    return getIdFromBytes(getBytes(tx, exclude_multi_sig=False))


def getIdFromBytes(data):
    """
    Generate data id.

    Args:
        data (:class:`bytes`): data as bytes sequence

    Returns:
        :class:`str`: id as hex string
    """
    return hexlify(secp256k1.hash_sha256(data))


def getBytes(tx, **options):
    """
    Hash transaction.

    Args:
        tx (:class:`dict` or :class:`Transaction`):
            transaction object

    Returns:
        :class:`bytes`: bytes sequence
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


# Reference:
# - https://github.com/ArkEcosystem/AIPs/blob/master/AIPS/aip-11.md
# - https://github.com/ArkEcosystem/AIPs/blob/master/AIPS/aip-102.md
def serialize(tx, version=None, **options):
    """
    Serialize transaction.

    Args:
        tx (:class:`dict` or :class:`Transaction`):
            transaction object

    Returns:
        :class:`bytes`: bytes sequence
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
    # "vendorFieldLength" = 255 since height 8,128,000
    vendorField = vendorField[:255]

    # common part
    pack("<BBB", buf, (0xff, version, cfg.pubkeyHash))
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
    if "signature" in tx and not options.get("exclude_sig", False):
        pack_bytes(buf, unhexlify(tx["signature"]))

    if not options.get("exclude_second_sig", False):
        if "signSignature" in tx:
            pack_bytes(buf, unhexlify(tx["signSignature"]))
        elif "secondSignature" in tx:
            pack_bytes(buf, unhexlify(tx["secondSignature"]))

    if "signatures" in tx and not options.get("exclude_multi_sig", False):
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
            recipientId = str(tx["recipientId"]) if not isinstance(
                    tx["recipientId"], bytes
                ) else \
                tx["recipientId"]
            recipientId = base58.b58decode_check(recipientId)
        except Exception:
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
                delegatePublicKey = delegatePublicKey.replace("+", "01")\
                                    .replace("-", "00")
                pack_bytes(buf, unhexlify(delegatePublicKey))
        else:
            raise Exception("no up/down vote given")

    # Multisignature registration
    elif _type == 4:
        multiSignature = asset.get("multiSignature", False)
        if multiSignature:
            pack(
                "<BB", buf,
                (multiSignature["min"], len(multiSignature["publicKeys"]))
            )
            pack_bytes(
                buf, b"".join(
                    [unhexlify(sig) for sig in multiSignature["publicKeys"]]
                )
            )

    # IPFS
    elif _type == 5:
        try:
            ipfs = str(asset["ipfs"]) if not isinstance(
                    asset["ipfs"], bytes
                ) else asset["ipfs"]
            data = base58.b58decode(ipfs)
        except Exception as e:
            raise Exception("bad ipfs autentification\n%r" % e)
        pack_bytes(buf, data)

    # multipayment
    elif _type == 6:
        try:
            items = [
                (p["amount"], base58.b58decode_check(
                    str(p["recipientId"]) if not isinstance(
                        p["recipientId"], bytes
                    ) else p["recipientId"]
                )) for p in asset.get("payments", {})
            ]
        except Exception:
            raise Exception("error in recipientId address list")
        result = pack("<I", buf, (len(items), ))
        for amount, address in items:
            pack("<Q", buf, (amount, ))
            pack_bytes(buf, address)

    # delegate resignation
    elif _type == 7:
        pass

    # HTLC lock
    elif _type == 8:
        try:
            recipientId = str(tx["recipientId"]) if not isinstance(
                tx["recipientId"], bytes
            ) else tx["recipientId"]
            recipientId = base58.b58decode_check(recipientId)
        except Exception:
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
