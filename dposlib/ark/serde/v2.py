# -*- coding: utf-8 -*-

import base58
from dposlib.util.bin import unhexlify, pack, pack_bytes


# https://github.com/ArkEcosystem/AIPs/blob/master/AIPS/aip-11.md

# transfer
def _1_0(tx, buf):
    try:
        recipientId = \
            str(tx["recipientId"]) \
            if not isinstance(tx["recipientId"], bytes) \
            else tx["recipientId"]
        recipientId = base58.b58decode_check(recipientId)
    except Exception:
        raise Exception("no recipientId defined")
    pack(
        "<QI", buf, (
            int(tx.get("amount", 0)),
            int(tx.get("expiration", 0))
        )
    )
    pack_bytes(buf, recipientId)


# secondSignature registration
def _1_1(tx, buf):
    asset = tx.get("asset", {})
    if "signature" in asset:
        secondPublicKey = asset["signature"]["publicKey"]
    else:
        raise Exception("no secondSecret or secondPublicKey given")
    pack_bytes(buf, unhexlify(secondPublicKey))


# delegate registration
def _1_2(tx, buf):
    asset = tx.get("asset", {})
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
def _1_3(tx, buf):
    asset = tx.get("asset", {})
    delegatePublicKeys = asset.get("votes", False)
    if delegatePublicKeys:
        pack("<B", buf, (len(delegatePublicKeys), ))
        for delegatePublicKey in delegatePublicKeys:
            delegatePublicKey = delegatePublicKey.replace("+", "01") \
                                .replace("-", "00")
            pack_bytes(buf, unhexlify(delegatePublicKey))
    else:
        raise Exception("no up/down vote given")


# Multisignature registration
def _1_4(tx, buf):
    asset = tx.get("asset", {})
    multiSignature = asset.get("multiSignature", False)
    if multiSignature:
        pack(
            "<BB", buf, (
                multiSignature["min"],
                len(multiSignature["publicKeys"])
            )
        )
        pack_bytes(
            buf, b"".join(
                [unhexlify(sig) for sig in multiSignature["publicKeys"]]
            )
        )


# IPFS
def _1_5(tx, buf):
    asset = tx.get("asset", {})
    try:
        ipfs = \
            str(asset["ipfs"]) \
            if not isinstance(asset["ipfs"], bytes) \
            else asset["ipfs"]
    except Exception as e:
        raise Exception("bad ipfs hash\n%r" % e)
    pack_bytes(buf, base58.b58decode(ipfs))


# multipayment
def _1_6(tx, buf):
    asset = tx.get("asset", {})
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
    pack("<H", buf, (len(items), ))
    for amount, address in items:
        pack("<Q", buf, (amount, ))
        pack_bytes(buf, address)


# delegate resignation
def _1_7(tx, buf):
    pass


# https://github.com/ArkEcosystem/AIPs/blob/master/AIPS/aip-102.md

# HTLC lock
def _1_8(tx, buf):
    asset = tx.get("asset", {})
    try:
        recipientId = \
            str(tx["recipientId"]) \
            if not isinstance(tx["recipientId"], bytes) \
            else tx["recipientId"]
        recipientId = base58.b58decode_check(recipientId)
    except Exception:
        raise Exception("no recipientId defined")
    lock = asset.get("lock", False)
    expiration = lock.get("expiration", False)
    if not lock or not expiration:
        raise Exception("no lock nor expiration data found")
    pack("<Q", buf, (int(tx.get("amount", 0)),))
    pack_bytes(buf, unhexlify(lock["secretHash"]))
    pack("<BI", buf, (int(expiration["type"]), int(expiration["value"])))
    pack_bytes(buf, recipientId)


# HTLC claim
def _1_9(tx, buf):
    asset = tx.get("asset", {})
    claim = asset.get("claim", False)
    if not claim:
        raise Exception("no claim data found")
    pack_bytes(buf, unhexlify(claim["lockTransactionId"]))
    pack_bytes(buf, claim["unlockSecret"].encode("utf-8"))


# HTLC refund
def _1_10(tx, buf):
    asset = tx.get("asset", {})
    refund = asset.get("refund", False)
    if not refund:
        raise Exception("no refund data found")
    pack_bytes(buf, unhexlify(refund["lockTransactionId"]))


# solar-network burn transaction
def _2_0(tx, buf):
    dict.__setitem__(tx, "fee", 0)
    pack("<Q", buf, (int(tx.get("amount", 0)), ))


# https://ark.dev/docs/core/transactions/transaction-types/entity
def _2_6(tx, buf):
    asset = tx.get("asset", {})
    data = asset.get("data", {})

    registrationId = unhexlify(asset.get("registrationId", ""))

    try:
        ipfs = data.get("ipfsData", "")
        ipfs = \
            str(ipfs).encode("utf-8") if not isinstance(ipfs, bytes) \
            else ipfs
    except Exception as e:
        raise Exception("bad ipfs hash\n%r" % e)
    try:
        name = data.get("name", "")
        name = \
            str(name).encode("utf-8") if not isinstance(name, bytes) \
            else name
    except Exception as e:
        raise Exception("bad entity name\n%r" % e)

    pack(
        "<BBBB", buf, (
            int(asset.get("type", 0)),
            int(asset.get("subType", 0)),
            int(asset.get("action", 0)),
            len(registrationId)
        )
    )
    pack_bytes(buf, registrationId)
    pack("<B", buf, (len(name), ))
    pack_bytes(buf, name)
    pack("<B", buf, (len(ipfs), ))
    pack_bytes(buf, ipfs)
