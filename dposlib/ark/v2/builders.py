# -*- coding: utf-8 -*-
# © Toons

import hashlib

from dposlib import rest
from dposlib.ark import crypto
from dposlib.blockchain import cfg, slots
from dposlib.blockchain.tx import Transaction
from dposlib.util.bin import hexlify


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
    return registerSecondPublicKey(crypto.getKeys(secondSecret)["publicKey"])


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
        signatures=[]
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
