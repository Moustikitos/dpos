# -*- coding: utf-8 -*-

"""
ARK.io specific package.

See [Ark API documentation](
    https://api.ark.dev/public-rest-api/getting-started
) to see how to use http calls.

```python
>>> import dposlib
>>> from dposlib import rest
>>> rest.use("ark")
True
>>> # reach http://api.ark.io/api/delegates/arky endpoint using GET
>>> # HTTP request builder
>>> rest.GET.api.delegates.arky()["username"]
'arky'
>>> dlgt = dposlib.core.api.Delegate("arky")
>>> dlgt.forged
{u'rewards': 397594.0, u'total': 401908.71166083, u'fees': 4314.71166083}
>>> dposlib.core.crypto.getKeys("secret")["publicKey"]
'03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de933'
>>> dposlib.core.transfer(
...     1, "ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE",
...     u"\u2728 simple transfer vendorField"
... )
{
  "amount": 100000000,
  "asset": {},
  "recipientId": "ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE",
  "type": 0,
  "vendorField": "\u2728 simple transfer vendorField",
  "version": 1
}
>>> dposlib.core.htlcLock(
...     1, "ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE",
...     "my secret lock", expiration=12,
...     vendorField=u"\u2728 simple htlcLock vendorField"
... )
{
  "amount": 100000000,
  "asset": {
    "lock": {
      "secretHash":
        "dbaed2f2747c7aa5a834b082ccb2b648648758a98d1a415b2ed9a22fd29d47cb",
      "expiration": {
        "type": 1,
        "value": 82567745
      }
    }
  },
  "network": 23,
  "recipientId": "ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE",
  "type": 8,
  "typeGroup": 1,
  "vendorField": "\u2728 simple htlcLock vendorField",
  "version": 2
}
```
"""

import io
import os
import sys
import pprint

from datetime import datetime, timezone
from importlib import import_module

from dposlib import rest, cfg, HOME, FROZEN
from dposlib.ark import crypto, api
from dposlib.ark.tx import Transaction
from dposlib.util.bin import hexlify, unhexlify
from dposlib.util.asynch import setInterval

from dposlib.ark import builders
from dposlib.ark.builders import broadcastTransactions


cfg.headers["API-Version"] = "3"

GETNAME = {
    1: {
        0: lambda tx:
            "legacyTransfer" if "sxp" in rest.cfg.network else "transfer",
        1: lambda tx: "secondSignature",
        2: lambda tx: "delegateRegistration",
        3: lambda tx:
            "legacyVote" if "sxp" in rest.cfg.network else "vote",
        4: lambda tx: "multiSignature",
        5: lambda tx: "ipfs",
        6: lambda tx:
            "transfer" if "sxp" in rest.cfg.network else "multiPayment",
        7: lambda tx: "delegateResignation",
        8: lambda tx: "htlcLock",
        9: lambda tx: "htlcClaim",
        10: lambda tx: "htlcRefund",
    },
    2: {
        # solar
        0: lambda tx: "burn",
        2: lambda tx: "vote",
        # ark
        6: lambda tx: (
            "entityRegistration" if tx["asset"]["action"] == 0 else
            "entityResignation" if tx["asset"]["action"] == 1 else
            "entityUpdate"
        )
    },
    # compendia
    100: {
        0: lambda tx: "stakeCreate",
        1: lambda tx: "stakeRedeem",
        2: lambda tx: "stakeCancel",
        3: lambda tx: "stakeExtend"
    },
    101: {
        0: lambda tx: "setFile"
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
    "memo": str,
    "MultiSignatureAddress": str,
    "multiSignatureAddress": str,
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

DAEMON_PEERS = None


def _load_builders():
    builders.CACHE.clear()
    __all__.clear()

    __all__.extend([
        api, cfg, rest, crypto,
        hexlify, unhexlify, broadcastTransactions,
    ])

    for name in [
        # generic transaction builder names [implemented]
        "transfer", "registerSecondSecret", "registerSecondPublicKey",
        "registerAsDelegate", "upVote", "downVote", "switchVote",
        "registerMultiSignature", "registerIpfs", "multiPayment",
        "delegateResignation", "htlcSecret", "htlcLock", "htlcClaim",
        "htlcRefund",
        # ark specific transaction builder [implemented]
        "entityRegister", "entityUpdate", "entityResign",
        # solar specific transaction builder names [implemented]
        "burn", "multiTransfer",
        # TODO: compendia specific transaction names
        "stakeCreate", "stakeCancel", "stakeExtend", "stakeRedeem",
        "setFile",
    ]:
        try:
            func = builders._getbldr(name)
            setattr(sys.modules[__name__], name, func)
        except NotImplementedError:
            pass
        else:
            __all__.append(func)


def _write_module(path, configuration={}, fees={}):
    if FROZEN:
        return
    with io.open(path, "w", encoding="utf-8") as module:
        module.write(
            "# -*- coding: utf-8 -*-\n"
            "# automatically generated by dposlib.ark package\n\n"
        )
        module.write("configuration = ")
        module.write(pprint.pformat(configuration))
        module.write("\nfees = ")
        module.write(pprint.pformat(fees))
        module.write("\n")


def _select_peers():
    peers = []
    candidates = rest.GET.api.peers(
        version=cfg.version, orderBy="height:desc"
    ).get("data", [])
    for candidate in candidates:
        api_port = -1
        for key, value in candidate.get("ports", {}).items():
            if key.endswith("/core-api"):
                api_port = value
                break
        if api_port > 0:
            peers.append("http://%s:%s" % (candidate["ip"], api_port))
            if len(peers) >= cfg.broadcast:
                break
    if len(peers):
        cfg.peers = peers


def init(seed=None):
    """
    Blockchain initialisation. It stores root values in `cfg` module.
    """
    global DAEMON_PEERS
    NETWORK = getattr(cfg, "network", "dark")
    # configure cold package path and fils according to installation
    if FROZEN:
        path_module = os.path.join(HOME, NETWORK + ".py")
        package_path = NETWORK
    else:
        path_module = os.path.join(
            os.path.join(__path__[0], "cold"), NETWORK + ".py"
        )
        package_path = __package__ + ".cold." + NETWORK
    path_module = os.path.normpath(path_module)

    CONFIG = FEES = {}
    # if network connection available
    if getattr(cfg, "hotmode", True):
        CONFIG = rest.GET.api.node.configuration(peer=seed)
        # nethash must be added before next api endpoint call
        cfg.headers["nethash"] = CONFIG["data"]["nethash"]
        # since ark v2.4 fee statistics moved to ~/api/node/fees endpoint
        FEES = rest.GET.api.node.fees(peer=seed)
        # write configuration in python module, overriding former one
        _write_module(path_module, CONFIG, FEES)
    else:
        try:
            new_pkg = import_module(package_path)
            if hasattr(sys.modules[__package__], "cold"):
                del sys.modules[__package__].cold
            sys.modules[__package__].cold = new_pkg
        except ImportError:
            try:
                sys.modules[__package__].cold = import_module(
                    __package__ + ".cold." + NETWORK
                )
            except Exception:
                raise Exception("cold start not possible")
        finally:
            CONFIG = sys.modules[__package__].cold.configuration
            FEES = sys.modules[__package__].cold.fees

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
    # on solar block time is blockTime
    cfg.blocktime = constants.get("blockTime", constants.get("blocktime"))
    cfg.begintime = datetime.strptime(
        constants["epoch"], "%Y-%m-%dT%H:%M:%S.000Z"
    ).replace(tzinfo=timezone.utc)
    cfg.blockreward = float(constants["reward"])/100000000
    # since ark v2.4 wif and slip44 are provided by network
    if "wif" in data:
        cfg.wif = "%x" % data["wif"]
    if "slip44" in data:
        cfg.slip44 = str(data["slip44"])
    # -- static fee management ------------------------------------------------
    cfg.fees = constants.get("fees", {})
    # -- dynamic fee management -----------------------------------------------
    # since v2.1 dynamicFees offsets are in "transactionPool" field
    cfg.doffsets = data.get("transactionPool", {})\
                       .get("dynamicFees", {}).get("addonBytes", {})
    # since ark v2.6 fee statistic structure is a dictionary
    cfg.feestats = FEES["data"]
    # activate dynamic fees
    Transaction.useDynamicFee("avgFee")
    # -- schnorr signature tweak ----------------------------------------------
    # on solar-network, tx versinon 3 only accept bip340 schnorr signatures
    cfg.bip340 = constants.get("bip340", False) or \
        (cfg.token in ["tSXP", "SXP"] and cfg.txversion >= 3)
    # -- network connection management ----------------------------------------
    # change peers every 30 seconds
    if getattr(cfg, "hotmode", False):
        DAEMON_PEERS = setInterval(30)(_select_peers)()
    # load transaction builders
    _load_builders()

    return True


def stop():
    """
    Stop daemon initialized by `init` call.
    """
    global DAEMON_PEERS
    if DAEMON_PEERS is not None:
        DAEMON_PEERS.set()


__all__ = [
    api, cfg, rest, crypto,
    hexlify, unhexlify, broadcastTransactions
]
