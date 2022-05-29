# -*- coding: utf-8 -*-

import base58
from dposlib.util.bin import unhexlify, hexlify, pack, pack_bytes


# solar vote transaction
def _1_3(tx, buf):
    asset = tx.get("asset", {})
    usernames = asset.get("votes", False)
    if usernames:
        pack("<B", buf, (len(usernames), ))
        for username in usernames:
            pack_bytes(buf, unhexlify(
                ("%02x" % len(username)) +
                ("01" if username.startswith("+") else "00") +
                hexlify(username[1:])
            ))
    else:
        raise Exception("no up/down vote given")


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
    secretHash = unhexlify(lock["secretHash"])
    pack("<QB", buf, (int(tx.get("amount", 0)), len(secretHash)))
    pack_bytes(buf, secretHash)
    pack("<BI", buf, (int(expiration["type"]), int(expiration["value"])))
    pack_bytes(buf, recipientId)


# HTLC claim
def _1_9(tx, buf):
    asset = tx.get("asset", {})
    claim = asset.get("claim", False)
    if not claim:
        raise Exception("no claim data found")
    unlockSecret = unhexlify(claim["unlockSecret"])
    pack("<B", buf, (claim["hashType"],))
    pack_bytes(buf, unhexlify(claim["lockTransactionId"]))
    pack("<B", buf, (len(unlockSecret),))
    pack_bytes(buf, unlockSecret)


# solar-network burn transaction
def _2_0(tx, buf):
    dict.__setitem__(tx, "fee", 0)
    pack("<Q", buf, (int(tx.get("amount", 0)), ))
