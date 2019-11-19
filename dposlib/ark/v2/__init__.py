# -*- coding: utf-8 -*-
# © Toons


import os
import pytz
import hashlib
from datetime import datetime

import dposlib
from dposlib import rest
from dposlib.ark import crypto
from dposlib.ark.v2 import api
from dposlib.blockchain import cfg, slots, Transaction
from dposlib.util.asynch import setInterval
from dposlib.util.data import loadJson
from dposlib.util.bin import hexlify, unhexlify

cfg.headers["API-Version"] = "2"

DAEMON_PEERS = None
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


class Config(object):

    # api endpoint to locate blockchain configuration and fees
    CFG = "api/node/configuration"
    FEE = "api/node/fees"

    begintime = property(
        lambda cls: pytz.utc.localize(
            datetime.strptime(constants["epoch"], "%Y-%m-%dT%H:%M:%S.000Z")
        ),
        None, None, ""
    )
    pubKeyHash = property(
        lambda cls: cls.data.get("version", None), None, None, ""
    )
    explorer = property(
        lambda cls: cls.data.get("explorer", None), None, None, ""
    )
    symbol = property(lambda cls: cls.data.get("symbol", None), None, None, "")
    token = property(lambda cls: cls.data.get("token", None), None, None, "")
    ports = property(
        lambda cls: dict(
            [k.split("/")[-1], v] for k, v in cls.data["ports"].items()
        ),
        None, None, ""
    )

    def __init__(self, peer=None):
        cfg_path = os.path.join(dposlib.ROOT, ".cold", __name__+".cfg")
        fee_path = os.path.join(dposlib.ROOT, ".cold", __name__+".fee")

        self.headers = {
            "Content-Type": "application/json",
            "API-Version": "2"
        }

        if peer is not None:
            self.cfg = rest.GET(*Config.CFG.split("/"), peer=peer)
            self.fee = rest.GET(*Config.FEE.split("/"), peer=peer)
            api.dumpJson(self.cfg, cfg_path)
            api.dumpJson(self.fee, fee_path)
        else:
            self.cfg = loadJson(cfg_path)
            self.fee = loadJson(fee_path)

        self.constants = cfg.get("constants", {})
        self.data = cfg.get("data", {})
        
        if len(self.data):
            self.headers["nethash"] = self.data["nethash"]

    def _getter(self, attr, path):
        if not hasattr(self, "_" + attr):
            setattr(self, "_" + attr, getattr(self, attr))
        return getattr(self, "_" + attr)


def select_peers():
    api_port = cfg.ports["core-api"]
    peers = []
    candidates = rest.GET.api.peers().get("data", [])
    for candidate in candidates:
        peer = "http://%s:%s" % (candidate["ip"], api_port)
        if candidate.get("version", "") > cfg.minversion:
            synced = rest.GET.api.node.status(peer=peer).get("data")
            if isinstance(synced, dict) and synced.get("synced", False):
                peers.append(peer)
        if len(peers) >= cfg.broadcast:
            break
    if len(peers):
        cfg.peers = peers


@setInterval(30)
def rotate_peers():
    select_peers()


def init():
    global DAEMON_PEERS

    if len(cfg.peers):
        data = rest.GET(*__CFG__.split("/")).get("data", {})
        cfg.hotmode = True
        api.dumpJson(
            data, os.path.join(dposlib.ROOT, ".cold", cfg.network+".v2.cfg")
        )
    # if no network connection, load basic confivuration from local folder
    else:
        cfg.hotmode = False
        data = loadJson(
            os.path.join(dposlib.ROOT, ".cold", cfg.network+".v2.cfg")
        )

    # no network connetcion neither local configuration files
    if data == {}:
        raise Exception("Initialization error")
    else:
        cfg.marker = hex(data["version"])[2:]
        cfg.pubKeyHash = data["version"]
        cfg.token = data["token"]
        cfg.symbol = data["symbol"]
        cfg.ports = dict(
            [k.split("/")[-1], v] for k, v in data["ports"].items()
        )
        cfg.headers["nethash"] = data["nethash"]
        cfg.explorer = data["explorer"]

        constants = data["constants"]
        cfg.delegate = constants["activeDelegates"]
        cfg.maxlimit = constants["block"]["maxTransactions"]
        cfg.maxTransactions = constants["block"]["maxTransactions"]
        cfg.blocktime = constants["blocktime"]
        cfg.begintime = pytz.utc.localize(
            datetime.strptime(constants["epoch"], "%Y-%m-%dT%H:%M:%S.000Z")
        )
        cfg.blockreward = constants["reward"]/100000000.
        cfg.fees = constants["fees"]

        # dynamic fee management
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
            [i["type"], i["fees"]] for i in data.get("feeStatistics", {})
        )
        # since ark v2.4 fee statistic moved to ~/api/node/fees endpoint
        if cfg.feestats == {}:
            if len(cfg.peers):
                fees = rest.GET(*__FEE__.split("/"))
                api.dumpJson(
                    fees,
                    os.path.join(dposlib.ROOT, ".cold", cfg.network+".v2.fee")
                )
            else:
                fees = loadJson(
                    os.path.join(dposlib.ROOT, ".cold", cfg.network+".v2.fee")
                )
            cfg.feestats = dict([
                int(i["type"]), {
                    "avgFee": int(i["avg"]),
                    "minFee": int(i["min"]),
                    "maxFee": int(i["min"]),
                }
            ] for i in fees.get("data", []))

        # since ark v2.4 wif and slip44 are provided by network
        if "wif" in data:
            cfg.wif = hex(data["wif"])[2:]
        if "slip44" in data:
            cfg.slip44 = str(data["slip44"])

        if len(cfg.peers):
            DAEMON_PEERS = rotate_peers()
        Transaction.useDynamicFee()


def stop():
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
    serialized = params.pop("serialized", False)
    chunk_size = params.pop("chunk_size", 20)
    report = []
    if serialized:
        transactions = [crypto.serialize(tx) for tx in transactions]
        for chunk in [
            transactions[i:i+chunk_size] for i in
            range(0, len(transactions), chunk_size)
        ]:
            pass
    else:
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
        block_height = \
            rest.GET.api.blockchain().get("data", {}).get("block", {})\
            .get("height", -block_remaining)
        expiration = int(block_height + block_remaining)

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
