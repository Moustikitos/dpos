# -*- coding: utf-8 -*-

from dposlib import rest, cfg
from dposlib.ark.tx import Transaction


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
    Transform a [`dposlib.ark.builders.upVote`](
        builders.md#dposlib.ark.builders.upVote
    ) transaction into a multivote one. It makes the transaction downvote
    former delegate if any and then apply new vote.

    Arguments:
        tx (dposlib.ark.tx.Transaction): upVote transaction.

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


# def burn(amount, vendorField=None):
#     """
#     Build a burn transaction.
#     ```

#     Args:
#         amount (float): transaction amount as human value.

#     Returns:
#         dposlib.ark.tx.Transaction: orphan transaction.
#     """
#     return Transaction(
#         type=0,
#         fee=0,
#         typeGroup=2,
#         amount=amount*100000000,
#         vendorField=vendorField,
#         version=cfg.txversion,
#     )
