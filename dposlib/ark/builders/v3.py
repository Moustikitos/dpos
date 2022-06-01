# -*- coding: utf-8 -*-

import hashlib
from dposlib import rest, cfg
from dposlib.ark import slots
from dposlib.ark.tx import Transaction
from dposlib.util.bin import hexlify


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


def upVote(*usernames):
    """
    Build an upvote transaction.

    Args:
        usernames (iterable): delegate usernames as str iterable.

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
    """
    Build a downvote transaction.

    Args:
        usernames (iterable): delegate usernames as str iterable.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction.
    """
    return Transaction(
        type=3,
        version=cfg.txversion,
        asset={
            "votes": ["-" + username for username in usernames]
        },
    )


def switchVote(tx, identifier=None):
    """
    Transform a [`dposlib.ark.builders.v3.upVote`](
        v3.md#dposlib.ark.builders.upVote
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
    identifier = identifier or tx["senderPublicKey"]
    if identifier is not None:
        wallet = rest.GET.api.wallets(identifier, returnKey="data")
        username = wallet.get("attributes", {}).get("vote", None)
        if username is None:
            pass
        elif "-" + username not in tx["asset"]["votes"]:
            tx["asset"]["votes"].insert(0, "-" + username)
        return tx
    else:
        raise Exception("orphan vote transaction can not be set as multivote")


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
        secret (str): passphrase used by htlc lock transaction.
        hash_type (int): hash method used.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction.
    """
    return Transaction(
        version=cfg.txversion,
        type=9,
        asset={
            "claim": {
                "hashType": hash_type,
                "lockTransactionId": txid,
                "unlockSecret": hexlify(htlcSecret(secret, hash_type))
            }
        }
    )


def burn(amount, vendorField=None):
    """
    Build a burn transaction.
    ```

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
