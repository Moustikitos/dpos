# -*- coding: utf-8 -*-

"""
QSLP specific package.
"""

import dposlib.ark

from dposlib import rest, cfg
from dposlib.ark import crypto, GETNAME, TYPING
from dposlib.ark.tx import Transaction
from dposlib.util.bin import hexlify, unhexlify
from dposlib.qslp import api

# --- TWEAKS --- inject the new definitions into the ark package
from dposlib.qslp import builders
import dposlib.ark.builders

for func in builders.__all__:
    name = func.__name__
    setattr(dposlib.ark.builders, name, getattr(builders, name))

del builders
# --- TWEAKS ---


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


from dposlib.ark.builders import (
    broadcastTransactions, transfer, registerSecondSecret,
    registerSecondPublicKey, registerAsDelegate, upVote, downVote,
    registerMultiSignature, registerIpfs, multiPayment, delegateResignation,
    htlcSecret, htlcLock, htlcClaim, htlcRefund,
    entityRegister, entityUpdate, entityResign,
    qslpGenesis, qslpBurn, qslpMint, qslpSend, qslpPause, qslpResume,
    qslpNewOwner, qslpFreeze, qslpUnFreeze,
    qslp2Genesis, qslp2Pause, qslp2Resume,
    qslp2NewOwner, qslp2AuthMeta, qslp2RevokeMeta,
    qslp2Clone, qslp2AddMeta, qslp2VoidMeta
)


__all__ = [
    api, cfg, rest, crypto,
    hexlify, unhexlify, broadcastTransactions,
    transfer, registerSecondSecret, registerSecondPublicKey,
    registerAsDelegate, upVote, downVote, registerMultiSignature,
    registerIpfs, multiPayment, delegateResignation,
    htlcSecret, htlcLock, htlcClaim, htlcRefund,
    entityRegister, entityUpdate, entityResign,
    qslpGenesis, qslpBurn, qslpMint, qslpSend, qslpPause, qslpResume,
    qslpNewOwner, qslpFreeze, qslpUnFreeze,
    qslp2Genesis, qslp2Pause, qslp2Resume,
    qslp2NewOwner, qslp2AuthMeta, qslp2RevokeMeta,
    qslp2Clone, qslp2AddMeta, qslp2VoidMeta
]
