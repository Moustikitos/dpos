# -*- coding: utf-8 -*-

import math
import hashlib
import collections

from functools import cmp_to_key
from operator import xor
from dposlib import cfg, rest
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


def upVote(*usernames, **weights):
    """
    Build an upvote transaction.

    Args:
        *usernames (iterable): delegate usernames as str iterable.
        **weights (mapping): username with ponderation. Vote weight will be
            computed in percent.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction.

    Raises:
        AssertionError: usernames and weights should not be mixed.

    ```python
    >>> dposlib.core.upVote("alpha", "bravo", "charlie").asset
    ... {'votes': OrderedDict([('bravo', 33.34), ('alpha', 33.33), ('charlie', 33.33)])}
    >>> dposlib.core.upVote(alpha=2, bravo=1, charlie=3).asset
    ... {'votes': OrderedDict([('charlie', 50.0), ('alpha', 33.33), ('bravo', 16.67)])}
    ```
    """
    assert xor(len(usernames), len(weights)), \
        "give username list or a vote weight mapping"

    remind = 10000  # 100.0 * 10 to be distributed
    votes = {}

    if len(weights):
        usernames = list(weights.keys())
        total = sum(weights.values())
        weights = dict(
            [u, (float(w) / total) * 10000] for u, w in weights.items()
        )
    else:
        usernames = [user for user in usernames if not user.startswith("-")]
        nb = len(usernames)
        weights = dict([user, remind // nb] for user in usernames)

    remind -= sum([math.trunc(w) for w in weights.values()])
    while remind > 0:
        weights[usernames[remind]] += 1
        remind -= 1

    sorter_fn = cmp_to_key(
        lambda a, b:
            -1 if a[1] > b[1] else 1 if b[1] > a[1] else
            1 if a[0] > b[0] else -1
    )
    votes = collections.OrderedDict(
        [u, math.trunc(w) / 100]
        for u, w in sorted(weights.items(), key=sorter_fn)
    )

    return Transaction(
        typeGroup=2,
        type=2,
        version=cfg.txversion,
        asset={
            "votes": votes
        },
    )


def legacyVote(*usernames):
    """
    Build an upvote transaction. Multiple usernames are allowed but not
    necessary supported by targeted dpos blockchain.

    Args:
        *usernames (iterable): delegate usernames as str iterable.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction.
    """
    return Transaction(
        type=3,
        version=cfg.txversion,
        asset={
            "votes": ["+" + username for username in usernames]
        },
    )


def downVote(*usernames):
    raise NotImplementedError(
        "downVote is not implemented for v3 transactions"
    )


def switchVote(tx, identifier=None):
    """
    Transform a [`dposlib.ark.builders.v3.legacyVote`](
        v3.md#dposlib.ark.builders.legacyVote
    ) transaction into a switchVote. It makes the transaction downvote
    former delegate if any and then apply new vote.
    Arguments:
        tx (dposlib.ark.tx.Transaction): upVote transaction.
        identifier (dposlib.ark.tx.Transaction): any identifier accepted by
            /api/wallets API endpoint. it could be a username, a wallet address
            or a publicKey.
    Returns:
        dposlib.ark.tx.Transaction: orphan transaction.
    """
    assert tx["typeGroup"] == 1, \
        "switch vote only available for legacy vote transactions"
    identifier = identifier or tx["senderPublicKey"]
    if identifier is not None:
        wallet = rest.GET.api.wallets(identifier, returnKey="data")
        usernames = list(wallet.get("votingFor", {}).keys())
        for user in [u for u in usernames if u not in tx["asset"]["votes"]]:
            tx["asset"]["votes"].insert(0, "-" + user)
        return tx
    else:
        raise Exception("orphan vote transaction can not be set as multivote")


def transfer(*pairs, **kwargs):
    """
    Build transfer transaction. Emoji can be included in transaction
    vendorField using unicode formating.

    ```python
    >>> u"message with sparkles \u2728"
    ```

    Args:
        vendorField (str): vendor field message.
        *pairs (iterable): recipient-amount pair iterable.
        **kwargs: arbitrary transaction field values.

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


multiTransfer = transfer


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
