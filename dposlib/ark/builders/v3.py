# -*- coding: utf-8 -*-

import hashlib

from functools import cmp_to_key
from operator import xor
from dposlib import cfg
from dposlib.ark import slots
from dposlib.ark.tx import Transaction
from dposlib.util.bin import hexlify, HEX, checkAddress


HtlcSecretHashType = {
    0: hashlib.sha256,
    1: hashlib.sha384,
    2: hashlib.sha512,
    3: hashlib.sha3_256,
    4: hashlib.sha3_384,
    5: hashlib.sha3_512,
    # Keccak256 = 6,
    # Keccak384 = 7,
    # Keccak512 = 8,
}


def legacyTransfer(amount, address, vendorField=None, expiration=0):
    """
    Build a transfer transaction. Emoji can be included in transaction
    vendorField using unicode formating.

    ```python
    >>> vendorField = u"message with sparkles \u2728"
    ```

    Args:
        amount (float): transaction amount in ark.
        address (str): valid recipient address.
        vendorField (str): vendor field message.
        expiration (float): time of persistance in hour.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction.
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


def upVote(*usernames, **weights):
    """
    Build an upvote transaction.

    Args:
        usernames (iterable): delegate usernames as str iterable.

    Kwargs:
        weight (mapping): username with ponderation. Vote weight will be
            computed in percent.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction.
    """
    assert xor(len(usernames), len(weights)), \
        "give username list or a vote weight mapping"

    remind = 10000  # 100.0 * 10
    votes = {}

    if len(weights):
        usernames = list(weights.keys())
        total = sum(weights.values())
        weights = dict([u, w / total] for u, w in weights.items())
    else:
        usernames = [user for user in usernames if not user.startswith("-")]
        nb = len(usernames)
        weights = dict([user, remind / 100 // nb] for user in usernames)

    remind -= sum([int(w * 100) for w in weights.values()])
    while remind > 0:
        weights[usernames[remind % nb]] += 0.01  # % nb not to necessary...
        remind -= 1

    sorter_fn = cmp_to_key(
        lambda a, b:
            -1 if a[1] > b[1] else 1 if b[1] > a[1] else
            1 if a[0] > b[0] else -1
    )
    votes = dict(sorted(weights.items(), key=sorter_fn))

    return Transaction(
        typeGroup=2,
        type=2,
        version=cfg.txversion,
        asset={
            "votes": votes
        },
    )


def downVote(*usernames):
    raise NotImplementedError(
        "downVote is not implemented for v3 transactions"
    )


def switchVote(tx, identifier=None):
    raise NotImplementedError(
        "switchVote is not implemented for v3 transactions"
    )


def transfer(*pairs, **kwargs):
    """
    Build transfer transaction. Emoji can be included in transaction
    vendorField using unicode formating.

    ```python
    >>> u"message with sparkles \u2728"
    ```

    Args:
        pairs (iterable): recipient-amount pair iterable.
        vendorField (str): vendor field message.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction.
    """
    if len(pairs) == 2:
        try:
            checkAddress(pairs[-1])
        except Exception:
            pass
        else:
            pairs = (pairs, )

    return Transaction(
        version=cfg.txversion,
        type=6,
        vendorField=kwargs.get("vendorField", None),
        asset={
            "transfers": [
                {"amount": int(a*100000000), "recipientId": r}
                for a, r in pairs
            ]
        }
    )


multiPayment = multiTransfer = transfer


def htlcSecret(secret, hash_type=0):
    """
    Compute an HTLC secret from passphrase.

    Args:
        secret (str): passphrase.
        hash_type (int): hash method used.

    Returns:
        bytes: HTLC secret.
    """
    return HtlcSecretHashType[hash_type](
        secret if isinstance(secret, bytes) else
        secret.encode("utf-8")
    ).digest()


def htlcLock(
    amount, address, secret, expiration=24, vendorField=None, hash_type=0
):
    """
    Build an HTLC lock transaction. Emoji can be included in transaction
    vendorField using unicode formating.

    ```python
    >>> vendorField = u"message with sparkles \u2728"
    ```

    Args:
        amount (float): transaction amount in ark.
        address (str): valid recipient address.
        secret (str): lock passphrase.
        expiration (float): transaction validity in hour.
        vendorField (str): vendor field message.
        hash_type (int): hash method used.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction.
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
                    HtlcSecretHashType[hash_type](
                        htlcSecret(secret, hash_type)
                    ).digest()
                ),
                "expiration": {
                    "type": 1,
                    "value": int(slots.getTime() + expiration*3600)
                }
            }
        }
    )


def htlcClaim(txid, secret, hash_type=0):
    """
    Build an HTLC claim transaction.

    Args:
        txid (str): htlc lock transaction id.
        secret (str): passphrase or hash used by htlc lock transaction.
        hash_type (int): hash method used.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction.
    """
    if not HEX.match(secret):
        secret = hexlify(htlcSecret(secret, hash_type))
    return Transaction(
        version=cfg.txversion,
        type=9,
        asset={
            "claim": {
                "hashType": hash_type,
                "lockTransactionId": txid,
                "unlockSecret": secret
            }
        }
    )


def burn(amount, vendorField=None):
    """
    Build a burn transaction.

    Args:
        amount (float): transaction amount as human value.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction.
    """
    return Transaction(
        type=0,
        fee=0,
        typeGroup=2,
        amount=amount*100000000,
        vendorField=vendorField,
        version=cfg.txversion,
    )
