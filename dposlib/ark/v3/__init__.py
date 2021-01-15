# -*- coding: utf-8 -*-
# © Toons

import os
import sys
import pytz

from datetime import datetime
from importlib import import_module

from dposlib.ark.v2 import *
from dposlib.ark.v2 import _write_module
from dposlib import HOME, rest
from dposlib.blockchain import cfg
from dposlib.blockchain.tx import Transaction
from dposlib.util.asynch import setInterval

from usrv import req


cfg.headers["API-Version"] = "3"

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
    # 11: "entityRegistration",
    # 12: "entityResignation",
    # 13: "entityUpdate"
}

TYPING = {
    "amount": int,
    "asset": dict,
    "blockId": str,
    "confirmations": int,
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
    peers = []
    candidates = rest.GET.api.peers(
        version=cfg.version, orderBy="height:desc"
    ).get("data", [])
    for candidate in candidates:
        api_port = candidate.get(
            "plugins", {}
        ).get("@arkecosystem/core-api", {}).get("port", False)
        if api_port:
            peers.append("http://%s:%s" % (candidate["ip"], api_port))
            if len(peers) >= cfg.broadcast:
                break
    if len(peers):
        cfg.peers = peers


@setInterval(30)
def _rotate_peers():
    _select_peers()


def init(seed=None):
    """
    Blockchain initialisation. It stores root values in :mod:`cfg` modules.
    """
    global DAEMON_PEERS
    NETWORK = getattr(cfg, "network", "dark")
    # configure cold package path and fils according to installation
    if ".zip" in __file__ or ".egg" in __file__:
        # --> module loaded from zip or egg file
        path_module = os.path.join(HOME, NETWORK + ".py")
        package_path = NETWORK
    else:
        # --> module loaded from python package
        path_module = os.path.join(
            os.path.join(__path__[0], "cold"), NETWORK + ".py"
        )
        package_path = __package__ + ".cold." + NETWORK
    path_module = os.path.normpath(path_module)

    # if network connection available
    if getattr(cfg, "hotmode", True):
        CONFIG = req.GET.api.node.configuration(peer=seed)
        # nethash must be added before next api endpoint call
        cfg.headers["nethash"] = CONFIG["data"]["nethash"]
        FEES = req.GET.api.node.fees(peer=seed)
        # write configuration in python module, overriding former one
        _write_module(path_module, CONFIG, FEES)
    else:
        # remove cold package
        if hasattr(sys.modules[__package__], "cold"):
            del sys.modules[__package__].cold
        # load cold package
        try:
            sys.modules[__package__].cold = import_module(
                package_path
            )
            CONFIG = sys.modules[__package__].cold.configuration
            FEES = sys.modules[__package__].cold.fees
        except Exception:
            CONFIG = FEES = {}

    # no network connetcion neither local configuration files
    if "data" not in CONFIG:
        raise Exception("no data available")

    data = CONFIG.get("data", {})
    constants = data["constants"]

    # -- root configuration ---------------------------------------------------
    cfg.version = data.get("core", {}).get("version", "?")
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
    cfg.blockreward = float(constants["reward"])/100000000
    # since ark v2.4 wif and slip44 are provided by network
    if "wif" in data:
        cfg.wif = "%x" % data["wif"]
    if "slip44" in data:
        cfg.slip44 = str(data["slip44"])
    # -- static fee management ------------------------------------------------
    cfg.fees = constants["fees"]
    # -- dynamic fee management -----------------------------------------------
    # since v2.1 dynamicFees offsets are in "transactionPool" field
    cfg.doffsets = data.get(
        "transactionPool", {}
    ).get("dynamicFees", {}).get("addonBytes", {})
    # since ark v2.4 fee statistics moved to ~/api/node/fees endpoint
    fees = FEES["data"]
    # since ark v2.6 fee statistic structure is a dictionary
    if isinstance(fees, dict):
        NUM = dict([v, k] for k, v in TRANSACTIONS.items())
        # for i, d in fees.items():
        stats = dict(
            [NUM[k], {
                "avgFee": int(v["avg"]),
                "minFee": int(v["min"]),
                "maxFee": int(v["max"]),
            }] for k, v in fees.get("1", {}).items()
        )
        setattr(cfg, "feestats", stats)
    # activate dynamic fees
    Transaction.useDynamicFee("avgFee")
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


__all__ = [
    "api",
    "crypto",
    "hexlify", "unhexlify",
    "Transaction",
    "broadcastTransactions",
    "transfer", "registerSecondSecret", "registerSecondPublicKey",
    "registerAsDelegate", "upVote", "downVote", "registerMultiSignature",
    "registerIpfs", "multiPayment", "delegateResignation",
    "htlcSecret", "htlcLock", "htlcClaim", "htlcRefund"
]
