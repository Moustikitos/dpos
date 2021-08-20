# -*- coding: utf-8 -*-
# © Toons

from dposlib import rest
from dposlib.blockchain.tx import Transaction


MAGISTRATE = {
    "business": 0,
    "product": 1,
    "plugin": 2,
    "module": 3,
    "delegate": 4
}


def entityRegister(name, type="business", subtype=0, ipfsData=None):
    asset = {
        "type": MAGISTRATE[type],
        "subType": subtype,
        "action": 0,
        "data": {
            "name":
                name.decode("utf-8")
                if isinstance(name, bytes)
                else name,
        }
    }

    if ipfsData is not None:
        asset["data"]["ipfsData"] = ipfsData

    return Transaction(
        version=rest.cfg.txversion,
        typeGroup=2,
        type=6,
        asset=asset
    )


def entityUpdate(registrationId, ipfsData, name=None):
    asset = rest.GET.api.transactions(
        registrationId
    ).get("data", {}).get("asset", {})

    asset["action"] = 1
    asset["registrationId"] = registrationId
    asset["data"] = {"ipfsData": ipfsData}

    if name is not None:
        asset["data"]["name"] = name

    return Transaction(
        version=rest.cfg.txversion,
        typeGroup=2,
        type=6,
        asset=asset
    )


def entityResign(registrationId):
    asset = rest.GET.api.transactions(
        registrationId
    ).get("data", {}).get("asset", {})

    asset["action"] = 2
    asset["registrationId"] = registrationId
    asset["data"] = {}

    return Transaction(
        version=rest.cfg.txversion,
        typeGroup=2,
        type=6,
        asset=asset
    )


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