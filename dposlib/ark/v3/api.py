# -*- coding: utf-8 -*-
# © Toons

import dposlib
from dposlib.ark.v2.api import *

GET = dposlib.rest.GET


class Wallet(Wallet):

    @dposlib.blockchain.isLinked
    def upVote(self, *usernames):
        "See [`dposlib.ark.v2.upVote`](blockchain.md#upvote)."
        tx = dposlib.core.upVote(*usernames)
        if self.attributes.vote is not None:
            tx["asset"]["votes"].insert(0, "-" + self.attributes.vote)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))


class Delegate(Delegate):

    wallet = property(lambda cls: Wallet(cls.address), None, None, "")


if LEDGERBLUE:

    class Ledger(Ledger, Wallet):
        pass
