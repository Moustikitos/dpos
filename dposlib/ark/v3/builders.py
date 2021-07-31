# -*- coding: utf-8 -*-
# © Toons

from dposlib import rest


def multiVote(tx):
    if hasattr(tx, "senderPublicKey"):
        vote = rest.GET.api.wallets(tx["senderPublicKey"], returnKey="data")\
            .get("attributes")\
            .get("vote", None)
        if vote is None:
            pass
        else:
            tx["asset"]["votes"].insert(0, "-" + vote)
    return tx
