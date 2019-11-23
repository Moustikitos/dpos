# -*- coding: utf-8 -*-
# © Toons

import io
import os
import sys
import pytz
import pprint
import hashlib

from datetime import datetime
from importlib import import_module

from dposlib import rest, PY3, HOME
from dposlib.ark import crypto
from dposlib.ark.v2 import api
from dposlib.blockchain import cfg, slots, Transaction
from dposlib.util.asynch import setInterval
from dposlib.util.bin import hexlify, unhexlify

cfg.headers["API-Version"] = "2"

DAEMON_PEERS = None
CONFIG = FEES = {}
TRANSACTIONS = {
    0: "transfer",
    1: "secondSignature",
    2: "delegateRegistration",
    3: "vote",
    4: "multiSignature",
    5: "ipfs",
    6: "multiPayment",
    7: "delegateResignation",
    8: "htlcLock",
    9: "htlcClaim",
    10: "htlcRefund",
}
TYPING = {
    "amount": int,
    "asset": dict,
    "expiration": int,
    "fee": int,
    "id": str,
    "MultiSignatureAddress": str,
    "network": int,
    "nonce": int,
    "recipientId": str,
    "senderPublicKey": str,
    "senderId": str,
    "signature": str,
    "signSignature": str,
    "signatures": list,
    "timestamp": int,
    "timelockType": int,
    "timelock": int,
    "type": int,
    "typeGroup": int,
    "vendorField": str,
    "vendorFieldHex": str,
    "version": int,
}


def _select_peers():
    api_port = cfg.ports["core-api"]
    peers = []
    candidates = rest.GET.api.peers().get("data", [])
    for candidate in candidates:
        peer = "http://%s:%s" % (candidate["ip"], api_port)
        synced = rest.GET.api.node.status(peer=peer).get("data")
        if isinstance(synced, dict) and synced.get("synced", False):
            peers.append(peer)
        if len(peers) >= cfg.broadcast:
            break
    if len(peers):
        cfg.peers = peers


@setInterval(30)
def _rotate_peers():
    _select_peers()


def init(seed=None):
    """
    """
    global DAEMON_PEERS, CONFIG, FEES
    from_zip = ".zip" in __file__ or ".egg" in __file__

    if hasattr(sys.modules[__package__], "cold"):
        del sys.modules[__package__].cold
    try:
        sys.modules[__package__].cold = import_module(
            ((__package__ + ".cold.") if not from_zip else "") + cfg.network
        )
    except ImportError:
        CONFIG = rest.GET(* "api/node/configuration".split("/"), peer=seed)
        cfg.headers["nethash"] = CONFIG["data"]["nethash"]
        FEES = rest.GET(* "api/node/fees".split("/"), peer=seed)
        with io.open(
            os.path.join(
                os.path.join(__path__[0], "cold") if not from_zip else HOME,
                cfg.network + ".py"
            ),
            "w" if PY3 else "wb", **({"encoding": "utf-8"} if PY3 else {})
        ) as module:
            module.write("configuration = ")
            module.write(pprint.pformat(CONFIG))
            module.write("\nfees = ")
            module.write(pprint.pformat(FEES))
    else:
        CONFIG = getattr(sys.modules[__package__].cold, "configuration")
        FEES = getattr(sys.modules[__package__].cold, "fees")
        cfg.headers["nethash"] = CONFIG["data"]["nethash"]

    # no network connetcion neither local configuration files
    if "data" not in CONFIG:
        raise Exception("no data available")

    data = CONFIG.get("data", {})
    constants = data["constants"]

    # -- root configuration ---------------------------------------------------
    cfg.explorer = data["explorer"]
    cfg.marker = "%x" % data["version"]
    cfg.pubkeyHash = data["version"]
    cfg.token = data["token"]
    cfg.symbol = data["symbol"]
    cfg.ports = dict(
        [k.split("/")[-1], v] for k, v in data["ports"].items()
    )
    cfg.activeDelegates = constants["activeDelegates"]
    cfg.maxTransactions = constants["block"]["maxTransactions"]
    cfg.blocktime = constants["blocktime"]
    cfg.begintime = pytz.utc.localize(
        datetime.strptime(constants["epoch"], "%Y-%m-%dT%H:%M:%S.000Z")
    )
    cfg.blockReward = float(constants["reward"])/100000000
    # since ark v2.4 wif and slip44 are provided by network
    if "wif" in data:
        cfg.wif = "%x" % data["wif"]
    if "slip44" in data:
        cfg.slip44 = str(data["slip44"])

    # -- static fee management ------------------------------------------------
    cfg.fees = constants["fees"]

    # -- dynamic fee management -----------------------------------------------
    # on v2.0 dynamicFees are in "fees" field
    cfg.doffsets = cfg.fees.get("dynamicFees", {}).get("addonBytes", {})
    # on v2.1 dynamicFees are in "transactionPool" field
    cfg.doffsets.update(
        data.get("transactionPool", {})
        .get("dynamicFees", {})
        .get("addonBytes", {})
    )
    # before ark v2.4 dynamicFees statistics are in "feeStatistics" field
    cfg.feestats = dict(
        [i["type"], int(i["fees"])] for i in data.get("feeStatistics", {})
    )
    # since ark v2.4 fee statistics moved to ~/api/node/fees endpoint
    if cfg.feestats == {}:
        if isinstance(FEES, list):
            cfg.feestats = dict([
                int(i["type"]), {
                    "avgFee": int(i["avg"]),
                    "minFee": int(i["min"]),
                    "maxFee": int(i["max"]),
                }
            ] for i in FEES)
        # since ark v2.6 fee statistic structure is a dictionary
        elif isinstance(FEES, dict):
            NUM = dict([v, k] for k, v in TRANSACTIONS.items())
            cfg.feestats = dict([
                NUM[k], {
                    "avgFee": int(v["avg"]),
                    "minFee": int(v["min"]),
                    "maxFee": int(v["max"]),
                }
            ] for k, v in FEES.get("1", {}).items())
    # activate dynamic fees
    Transaction.useDynamicFee()
    # -- network connection management ----------------------------------------
    # change peers every 30 seconds
    if getattr(cfg, "hotmode", False):
        DAEMON_PEERS = _rotate_peers()

    return True


def stop():
    """
    Stop daemon initialized by ``init`` call.
    """
    global DAEMON_PEERS
    if DAEMON_PEERS is not None:
        DAEMON_PEERS.set()


# https://github.com/ArkEcosystem/AIPs/blob/master/AIPS/aip-16.md
def computeDynamicFees(tx):
    typ_ = tx.get("type", 0)
    version = tx.get("version", 0x01)

    vendorField = tx.get("vendorField", "")
    vendorField = \
        vendorField if isinstance(vendorField, bytes) else \
        vendorField.encode("utf-8")
    lenVF = len(vendorField)
    payload = crypto.serializePayload(tx)
    T = cfg.doffsets.get(TRANSACTIONS[typ_], 0)
    return int(
        (T + 55 + (4 if version >= 0x02 else 0) + lenVF + len(payload)) *
        Transaction.FMULT
    )


def broadcastTransactions(*transactions, **params):
    chunk_size = params.pop("chunk_size", cfg.maxTransactions)
    report = []
    for chunk in [
        transactions[i:i+chunk_size] for i in
        range(0, len(transactions), chunk_size)
    ]:
        response = rest.POST.api.transactions(transactions=chunk)
        report.append(response)
    return \
        None if len(report) == 0 else \
        report[0] if len(report) == 1 else \
        report


def transfer(amount, address, vendorField=None, expiration=0, version=1):
    if version > 1 and expiration > 0:
        block_remaining = expiration*60*60//rest.cfg.blocktime
        expiration = int(
            rest.GET.api.blockchain()
            .get("data", {}).get("block", {}).get("height", -block_remaining) +
            block_remaining
        )

    return Transaction(
        type=0,
        amount=amount*100000000,
        recipientId=address,
        vendorField=vendorField,
        version=version,
        expiration=None if version < 2 else expiration
    )


def registerSecondSecret(secondSecret, version=1):
    return registerSecondPublicKey(
        crypto.getKeys(secondSecret)["publicKey"], version=version
    )


def registerSecondPublicKey(secondPublicKey, version=1):
    return Transaction(
        type=1,
        version=version,
        asset={
            "signature": {
                "publicKey": secondPublicKey
            }
        }
    )


def registerAsDelegate(username, version=1):
    return Transaction(
        type=2,
        version=version,
        asset={
            "delegate": {
                "username": username
            }
        }
    )


def upVote(*usernames, **kwargs):
    try:
        votes = [
            "+"+rest.GET.api.delegates(username, returnKey="data")["publicKey"]
            for username in usernames
        ]
    except KeyError:
        raise Exception("one of delegate %s does not exist" %
                        ",".join(usernames))

    return Transaction(
        type=3,
        version=kwargs.get("version", 1),
        asset={
            "votes": votes
        },
    )


def downVote(*usernames, **kwargs):
    try:
        votes = [
            "-"+rest.GET.api.delegates(username, returnKey="data")["publicKey"]
            for username in usernames
        ]
    except KeyError:
        raise Exception("one of delegate %s does not exist" %
                        ",".join(usernames))

    return Transaction(
        type=3,
        version=kwargs.get("version", 1),
        asset={
            "votes": votes
        },
    )


# https://github.com/ArkEcosystem/AIPs/blob/master/AIPS/aip-18.md
def registerMultiSignature(min, *publicKeys, **kwargs):
    pkMin = crypto.getKeys(None, seed=unhexlify("%x" % min))["publicKey"]
    P = crypto.hex2EcPublicKey(pkMin).W
    for publicKey in publicKeys:
        P = P.curve.add_point(P, crypto.hex2EcPublicKey(publicKey).W)
    pkms = crypto.ecPublicKey2Hex(crypto.ECPublicKey(P))

    return Transaction(
        version=2,
        type=4,
        MultiSignatureAddress=crypto.getAddress(pkms),
        asset={
            "multiSignature": {
                "min": min,
                "publicKeys": publicKeys
            }
        },
    )


def registerIpfs(ipfs):
    return Transaction(
        version=2,
        type=5,
        asset={
            "ipfs": ipfs
        }
    )


def multiPayment(*pairs, **kwargs):
    return Transaction(
        version=2,
        type=6,
        vendorField=kwargs.get("vendorField", None),
        asset={
            "payments": [
                {"amount": a*100000000, "recipientId": r} for r, a in pairs
            ]
        }
    )


def delegateResignation():
    return Transaction(
        version=2,
        type=7
    )


def htlcSecret(secret):
    return hexlify(hashlib.sha256(
        secret if isinstance(secret, bytes) else
        secret.encode("utf-8")
    ).digest()[:16])


def htlcLock(amount, address, secret, expiration=24, vendorField=None):
    return Transaction(
        version=2,
        type=8,
        amount=amount*100000000,
        recipientId=address,
        vendorField=vendorField,
        asset={
            "lock": {
                "secretHash": hexlify(
                    hashlib.sha256(htlcSecret(secret).encode("utf-8")).digest()
                ),
                "expiration": {
                    "type": 1,
                    "value": int(slots.getTime() + expiration*60*60)
                }
            }
        }
    )


def htlcClaim(txid, secret):
    return Transaction(
        version=2,
        type=9,
        asset={
            "claim": {
                "lockTransactionId": txid,
                "unlockSecret": htlcSecret(secret)
            }
        }
    )


def htlcRefund(txid):
    return Transaction(
        version=2,
        type=10,
        asset={
            "refund": {
                "lockTransactionId": txid,
            }
        }
    )


__all__ = [
    "crypto",
    "Transaction",
    "broadcastTransactions",
    "transfer", "registerSecondSecret", "registerSecondPublicKey",
    "registerAsDelegate", "upVote", "downVote", "registerMultiSignature",
    "registerIpfs", "multiPayment", "delegateResignation",
    "htlcLock", "htlcClaim", "htlcRefund"
]
