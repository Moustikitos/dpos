# -*- coding: utf-8 -*-

"""
QSLP specific package.
"""

import dposlib.ark

from dposlib import rest, cfg
from dposlib.ark import crypto
from dposlib.ark.tx import Transaction
from dposlib.util.bin import hexlify, unhexlify
from dposlib.qslp import api

from dposlib.ark.builders import (
    broadcastTransactions, transfer, registerSecondSecret,
    registerSecondPublicKey, registerAsDelegate, upVote, downVote,
    registerMultiSignature, registerIpfs, multiPayment, delegateResignation,
    htlcSecret, htlcLock, htlcClaim, htlcRefund,
    entityRegister, entityUpdate, entityResign,
)


def _get_qslp_peers():
    setattr(cfg, "qsl_api", [
        "http://%s" % key for key in rest.req.GET.api.peerInfo(
            peer="https://aslp.qredit.dev"
        ).get("goodPeers", {})
    ])


def init(seed=None):
    """
    Blockchain initialisation. It stores root values in `cfg` module.
    """
    check = dposlib.ark.init(seed)
    if getattr(cfg, "hotmode", False):
        _get_qslp_peers()
    return check


def stop():
    """
    Stop daemon initialized by `init` call.
    """
    dposlib.ark.stop()


__all__ = [
    api, cfg, rest, crypto,
    hexlify, unhexlify, broadcastTransactions,
    transfer, registerSecondSecret, registerSecondPublicKey,
    registerAsDelegate, upVote, downVote, registerMultiSignature,
    registerIpfs, multiPayment, delegateResignation,
    htlcSecret, htlcLock, htlcClaim, htlcRefund,
    entityRegister, entityUpdate, entityResign,
]
