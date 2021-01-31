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

from dposlib import rest, PY3, HOME, FROZEN
from dposlib.ark import crypto
from dposlib.ark.v2 import api
from dposlib.blockchain import cfg, slots
from dposlib.blockchain.tx import Transaction
from dposlib.util.asynch import setInterval
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
        network.md#rest
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
    # since ark v2.4 fee statistics moved to ~/api/node/fees endpoint
    if cfg.feestats == {}:
        fees = FEES["data"]
        if isinstance(fees, list):
            cfg.feestats = dict([
                int(i["type"]), {
                    "avgFee": int(i["avg"]),
                    "minFee": int(i["min"]),
                    "maxFee": int(i["max"]),
                }
            ] for i in fees)
        # since ark v2.6 fee statistic structure is a dictionary
        elif isinstance(fees, dict):
            NUM = dict([v, k] for k, v in TRANSACTIONS.items())
            cfg.feestats = dict([
                NUM[k], {
                    "avgFee": int(v["avg"]),
                    "minFee": int(v["min"]),
                    "maxFee": int(v["max"]),
                }
            ] for k, v in fees.get("1", {}).items())
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


def broadcastTransactions(*transactions, **params):
    chunk_size = params.pop("chunk_size", cfg.maxTransactions)
    report = []
    for chunk in [
        transactions[i:i+chunk_size] for i in
        range(0, len(transactions), chunk_size)
    ]:
        report.append(rest.POST.api.transactions(transactions=chunk))
    return \
        None if len(report) == 0 else \
        report[0] if len(report) == 1 else \
        report


def transfer(amount, address, vendorField=None, expiration=0):
    """
    Build a transfer transaction. Emoji can be included in transaction
    vendorField using unicode formating.

    ```python
    >>> u"message with sparkles \u2728"
    ```

    Arguments:
        amount (float): transaction amount in ark
        address (str): valid recipient address
        vendorField (str): vendor field message
        expiration (float): time of persistance in hour
    Returns:
        transaction object
    """
    if cfg.txversion > 1 and expiration > 0:
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
        version=cfg.txversion,
        expiration=None if cfg.txversion < 2 else expiration
    )


def registerSecondSecret(secondSecret):
    """
    Build a second secret registration transaction.

    Arguments:
        secondSecret (str): passphrase
    Returns:
        transaction object
    """
    return registerSecondPublicKey(
        crypto.getKeys(secondSecret)["publicKey"], version=cfg.txversion
    )


def registerSecondPublicKey(secondPublicKey):
    """
    Build a second secret registration transaction.

    *You must own the secret issuing secondPublicKey*

    Arguments:
        secondPublicKey (str): public key as hex string
    Returns:
        transaction object
    """
    return Transaction(
        type=1,
        version=cfg.txversion,
        asset={
            "signature": {
                "publicKey": secondPublicKey
            }
        }
    )


def registerAsDelegate(username):
    """
    Build a delegate registration transaction.

    Arguments:
        username (str): delegate username
    Returns:
        transaction object
    """
    return Transaction(
        type=2,
        version=cfg.txversion,
        asset={
            "delegate": {
                "username": username
            }
        }
    )


def upVote(*usernames):
    """
    Build an upvote transaction.

    Arguments:
        usernames (iterable): delegate usernames as str
                              iterable
    Returns:
        transaction object
    """
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
        version=cfg.txversion,
        asset={
            "votes": votes
        },
    )


def downVote(*usernames):
    """
    Build a downvote transaction.

    Arguments:
        usernames (iterable): delegate usernames as str
                              iterable
    Returns:
        transaction object
    """
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
        version=cfg.txversion,
        asset={
            "votes": votes
        },
    )


# https://github.com/ArkEcosystem/AIPs/blob/master/AIPS/aip-18.md
def registerMultiSignature(minSig, *publicKeys):
    """
    Build a multisignature registration transaction.

    Args:
        minSig (int): minimum signature required
        publicKeys (list of str): public key list
    Returns:
        transaction object
    """
    return Transaction(
        version=cfg.txversion,
        type=4,
        MultiSignatureAddress=crypto.getAddress(
            crypto.getMultiSignaturePublicKey(
                minSig, *publicKeys
            )
        ),
        asset={
            "multiSignature": {
                "min": minSig,
                "publicKeys": publicKeys
            }
        },
    )


def registerIpfs(ipfs):
    """
    Build an IPFS registration transaction.

    Arguments:
        ipfs (str): ipfs DAG
    Returns:
        transaction object
    """
    return Transaction(
        version=cfg.txversion,
        type=5,
        asset={
            "ipfs": ipfs
        }
    )


def multiPayment(*pairs, **kwargs):
    """
    Build multi-payment transaction. Emoji can be included in transaction
    vendorField using unicode formating.

    ```python
    >>> u"message with sparkles \u2728"
    ```

    Arguments:
        pairs (iterable): recipient-amount pair iterable
        vendorField (str): vendor field message
    Returns:
        transaction object
    """
    return Transaction(
        version=cfg.txversion,
        type=6,
        vendorField=kwargs.get("vendorField", None),
        asset={
            "payments": [
                {"amount": int(a*100000000), "recipientId": r}
                for a, r in pairs
            ]
        }
    )


def delegateResignation():
    """
    Build a delegate resignation transaction.

    Returns:
        transaction object
    """
    return Transaction(
        version=cfg.txversion,
        type=7
    )


def htlcSecret(secret):
    """
    Compute an HTLC secret hex string from passphrase.

    Arguments:
        secret (str): passphrase
    Returns:
        transaction object
    """
    return hexlify(hashlib.sha256(
        secret if isinstance(secret, bytes) else
        secret.encode("utf-8")
    ).digest()[:16])


def htlcLock(amount, address, secret, expiration=24, vendorField=None):
    """
    Build an HTLC lock transaction. Emoji can be included in transaction
    vendorField using unicode formating.

    ```python
    >>> u"message with sparkles \u2728"
    ```

    Arguments:
        amount (float): transaction amount in ark
        address (str): valid recipient address
        secret (str): lock passphrase
        expiration (float): transaction validity in hour
        vendorField (str): vendor field message
    Returns:
        transaction object
    """
    return Transaction(
        version=cfg.txversion,
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
    """
    Build an HTLC claim transaction.

    Arguments:
        txid (str): htlc lock transaction id
        secret (str): passphrase used by htlc lock transaction
    Returns:
        transaction object
    """
    return Transaction(
        version=cfg.txversion,
        type=9,
        asset={
            "claim": {
                "lockTransactionId": txid,
                "unlockSecret": htlcSecret(secret)
            }
        }
    )


def htlcRefund(txid):
    """
    Build an HTLC refund transaction.

    Arguments:
        txid (str): htlc lock transaction id
    Returns:
        transaction object
    """
    return Transaction(
        version=cfg.txversion,
        type=10,
        asset={
            "refund": {
                "lockTransactionId": txid,
            }
        }
    )


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
