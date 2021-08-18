# -*- coding: utf-8 -*-
# © Toons

import io
import os
import sys
import pytz
import pprint

from datetime import datetime
from importlib import import_module

from dposlib import rest, PY3, HOME, FROZEN
from dposlib.ark import crypto
from dposlib.ark.v2 import api
from dposlib.blockchain import cfg
from dposlib.blockchain.tx import Transaction
from dposlib.util.asynch import setInterval
from dposlib.util.bin import hexlify, unhexlify

from dposlib.ark.v2.builders import (
    broadcastTransactions, transfer, registerSecondSecret,
    registerSecondPublicKey, registerAsDelegate, upVote, downVote,
    registerMultiSignature, registerIpfs, multiPayment, delegateResignation,
    htlcSecret, htlcLock, htlcClaim, htlcRefund
)

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

GETNAME = {
    1: {
        0: lambda tx: "transfer",
        1: lambda tx: "secondSignature",
        2: lambda tx: "delegateRegistration",
        3: lambda tx: "vote",
        4: lambda tx: "multiSignature",
        5: lambda tx: "ipfs",
        6: lambda tx: "multiPayment",
        7: lambda tx: "delegateResignation",
        8: lambda tx: "htlcLock",
        9: lambda tx: "htlcClaim",
        10: lambda tx: "htlcRefund",
    }
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
    api_port = cfg.ports["core-api"]
    peers = []
    candidates = rest.GET.api.peers(
        version=cfg.version,
        orderBy="height:desc"
    ).get("data", [])
    for candidate in candidates:
        peers.append("http://%s:%s" % (candidate["ip"], api_port))
        if len(peers) >= cfg.broadcast:
            break
    if len(peers):
        cfg.peers = peers


@setInterval(30)
def _rotate_peers():
    _select_peers()


def _write_module(path, configuration={}, fees={}):
    if FROZEN:
        return
    with io.open(
        path, "w" if PY3 else "wb", **({"encoding": "utf-8"} if PY3 else {})
    ) as module:
        module.write(
            "# -*- coding: utf-8 -*-\n"
            "# automatically generated by dposlib.ark.v2 module\n\n"
        )
        module.write("configuration = ")
        module.write(pprint.pformat(configuration))
        module.write("\nfees = ")
        module.write(pprint.pformat(fees))
        module.write("\n")


def init(seed=None):
    """
    Blockchain initialisation. It stores root values in [`rest.cfg`](
        blockchain.md#dposlibblockchaincfg
    ) modules.
    """
    global DAEMON_PEERS

    # configure cold package path and fils according to installation
    if ".zip" in __file__ or ".egg" in __file__:
        # --> module loaded from zip or egg file
        path_module = os.path.join(HOME, cfg.network + ".py")
        package_path = cfg.network
    else:
        # --> module loaded from python package
        path_module = os.path.join(
            os.path.join(__path__[0], "cold"), cfg.network + ".py"
        )
        package_path = __package__ + ".cold." + cfg.network
    path_module = os.path.normpath(path_module)

    # if network connection available
    if cfg.hotmode:
        CONFIG = rest.GET(* "api/node/configuration".split("/"), peer=seed)
        # nethash must be added before next api endpoint call
        cfg.headers["nethash"] = CONFIG["data"]["nethash"]
        FEES = rest.GET(* "api/node/fees".split("/"), peer=seed)
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
    cfg.version = data.get("core", {}).get("version", "2")
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
    # since v2.1 dynamicFees are in "transactionPool" field
    cfg.doffsets = data.get(
        "transactionPool", {}
    ).get("dynamicFees", {}).get("addonBytes", {})
    # since ark v2.4 fee statistics moved to ~/api/node/fees endpoint
    # since ark v2.6 fee statistic structure is a dictionary
    setattr(cfg, "feestats", FEES["data"])
    # activate dynamic fees
    Transaction.useDynamicFee()
    # -- network connection management ----------------------------------------
    # change peers every 30 seconds
    if getattr(cfg, "hotmode", False):
        DAEMON_PEERS = _rotate_peers()

    return True


def stop():
    """
    Stop daemon initialized by [`init`](blockchain.md#init) call.
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
