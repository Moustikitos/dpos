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
    """
    Build an entity registration.

    Arguments:
        name (str): entity name
        type (str): entity type
        subtype (int): entity subtype
        ipfsData (dict): ipfs data. Default to None.
    Returns:
        transaction object
    """
    asset = {
        "type": MAGISTRATE[type],
        "subType": subtype,
        "action": 0,
        "data": {
            "name":
                name.decode("utf-8") if isinstance(name, bytes)
                else name,
        }
    }

    if ipfsData is not None:
        asset["data"]["ipfsData"] = \
            ipfsData.decode("utf-8") if isinstance(ipfsData, bytes) \
            else ipfsData

    return Transaction(
        version=rest.cfg.txversion,
        typeGroup=2,
        type=6,
        asset=asset
    )


def entityUpdate(registrationId, ipfsData, name=None):
    """
    Build an entity update.

    Arguments:
        registrationId (str): registration id
        ipfsData (dict): ipfs data
        name (str, optional): entity name

    Returns:
        transaction object
    """
    asset = rest.GET.api.transactions(
        registrationId
    ).get("data", {}).get("asset", {})

    asset["action"] = 1
    asset["registrationId"] = registrationId
    asset["data"] = {
        "ipfsData":
            ipfsData.decode("utf-8") if isinstance(ipfsData, bytes)
            else ipfsData
    }

    if name is not None:
        asset["data"]["name"] = name

    return Transaction(
        version=rest.cfg.txversion,
        typeGroup=2,
        type=6,
        asset=asset
    )


def entityResign(registrationId):
    """
    Build an entity resignation.

    Arguments:
        registrationId (str): registration id

    Returns:
        transaction object
    """
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
    """
    Transform an `dposlib.ark.v2.builders.upVote` transaction into a multivote
    one. It makes the transaction downvote former delegate if any and then
    apply new vote.
    """
    if hasattr(tx, "senderPublicKey"):
        vote = rest.GET.api.wallets(tx["senderPublicKey"], returnKey="data")\
            .get("attributes")\
            .get("vote", None)
        if vote is None:
            pass
        else:
            tx["asset"]["votes"].insert(0, "-" + vote)
    return tx
