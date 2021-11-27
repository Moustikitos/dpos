# -*- coding: utf-8 -*-

import json

from dposlib import cfg
from dposlib.ark.tx import Transaction
from dposlib.qslp.api import GET


def qslpGenesis(de, sy, na, qt, du=None, no=None, pa=False, mi=False):
    args = dict(decimals=de, symbol=sy, name=na, quantity=qt)
    if du:
        args["uri"] = du
    if no:
        args["notes"] = no[:32]
    if pa:
        args["pausable"] = "true"
    if mi:
        args["mintable"] = "true"

    smartbridge = GET.api.vendor_aslp1_genesis(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=100000000,
        recipientId=cfg.master_address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslpBurn(tkid, qt, no=None):
    args = dict(tokenid=tkid, quantity=qt)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp1_burn(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=cfg.master_address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslpMint(tkid, qt, no=None):
    args = dict(tokenid=tkid, quantity=qt)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp1_mint(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=cfg.master_address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslpSend(tkid, qt, no=None):
    args = dict(tokenid=tkid, quantity=qt)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp1_send(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=cfg.master_address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslpPause(tkid, no=None):
    args = dict(tokenid=tkid)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp1_pause(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=cfg.master_address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslpResume(tkid, no=None):
    args = dict(tokenid=tkid)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp1_resume(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=cfg.master_address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslpNewOwner(address, tkid, no=None):
    args = dict(tokenid=tkid)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp1_newowner(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslpFreeze(address, tkid, no=None):
    args = dict(tokenid=tkid)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp1_freeze(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslpUnFreeze(address, tkid, no=None):
    args = dict(tokenid=tkid)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp1_unfreeze(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslp2Genesis(sy, na, du=None, no=None, pa=False):
    args = dict(symbol=sy, name=na)
    if du:
        args["uri"] = du
    if no:
        args["notes"] = no[:32]
    if pa:
        args["pausable"] = "true"

    smartbridge = GET.api.vendor_aslp2_genesis(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=100000000,
        recipientId=cfg.master_address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslp2Pause(tkid, no=None):
    args = dict(tokenid=tkid)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp2_pause(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=cfg.master_address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslp2Resume(tkid, no=None):
    args = dict(tokenid=tkid)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp2_resume(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=cfg.master_address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslp2NewOwner(address, tkid, no=None):
    args = dict(tokenid=tkid)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp2_newowner(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslp2AuthMeta(address, tkid, no=None):
    args = dict(tokenid=tkid)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp2_authmeta(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslp2RevokeMeta(address, tkid, no=None):
    args = dict(tokenid=tkid)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp2_revokemeta(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslp2Clone(tkid, no=None):
    args = dict(tokenid=tkid)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp2_clone(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=cfg.master_address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslp2AddMeta(tkid, na, dt, ch=None):
    args = dict(tokenid=tkid, name=na, data=dt)
    if ch:
        args["chunk"] = ch

    smartbridge = GET.api.vendor_aslp2_addmeta(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=cfg.master_address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslp2VoidMeta(tkid, tx):
    args = dict(tokenid=tkid, txid=tx)

    smartbridge = GET.api.vendor_aslp2_voidmeta(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=cfg.master_address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


__all__ = [
    qslpGenesis, qslpBurn, qslpMint, qslpSend, qslpPause, qslpResume,
    qslpNewOwner, qslpFreeze, qslpUnFreeze,
    qslp2Genesis, qslp2Pause, qslp2Resume,
    qslp2NewOwner, qslp2AuthMeta, qslp2RevokeMeta,
    qslp2Clone, qslp2AddMeta, qslp2VoidMeta
]
