# -*- coding: utf-8 -*-

import dposlib
from dposlib.ark.v2.api import *

GET = dposlib.rest.GET


class Wallet(Wallet):

    @dposlib.ark.isLinked
    def upVote(self, *usernames):
        "See [`dposlib.ark.v3.multiVote`](v3.md#multivote)."
        tx = dposlib.core.upVote(*usernames)
        if self.attributes.vote is not None:
            tx["asset"]["votes"].insert(0, "-" + self.attributes.vote)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @dposlib.ark.isLinked
    def createEntity(self, name, type="business", subtype=0, ipfsData=None):
        "See [`dposlib.ark.v3.entityRegister`](v3.md#entityregister)."
        tx = dposlib.core.entityRegister(name, type, subtype, ipfsData)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @dposlib.ark.isLinked
    def updateEntity(self, registrationId, ipfsData, name=None):
        "See [`dposlib.ark.v3.entityUpdate`](v3.md#entityupdate)."
        tx = dposlib.core.entityUpdate(registrationId, ipfsData, name)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @dposlib.ark.isLinked
    def resignEntity(self, registrationId):
        "See [`dposlib.ark.v3.entityResign`](v3.md#entityresign)."
        tx = dposlib.core.entityResign(registrationId)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))


class Delegate(Delegate):

    wallet = property(lambda cls: Wallet(cls.address), None, None, "")


if LEDGERBLUE:

    class Ledger(Ledger, Wallet):
        pass
