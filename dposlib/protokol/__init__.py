# -*- coding: utf-8 -*-

"""
[Protokol/NFT](https://www.protokol.com) platform specific package.
"""

import dposlib.ark

from dposlib.ark import init, stop, GETNAME, TYPING
from dposlib.protokol import serde, builders
from dposlib.util.bin import hexlify, unhexlify

from dposlib import rest, cfg
from dposlib.ark import crypto, api
from dposlib.ark.tx import Transaction

GETNAME[9000] = {
    0: lambda tx: "NFTRegisterCollection",
    1: lambda tx: "NFTCreate",
    2: lambda tx: "NFTTransfer",
    3: lambda tx: "NFTBurn"
}

# --- TWEAKS --- inject the new definitions into the ark package
import dposlib.ark.serde
import dposlib.ark.builders

for func in serde.__all__:
    name = func.__name__
    setattr(dposlib.ark.serde, name, getattr(serde, name))

for func in builders.__all__:
    name = func.__name__
    setattr(dposlib.ark.builders, name, getattr(builders, name))

del serde
del builders
# --- TWEAKS ---

from dposlib.ark.builders import (
    broadcastTransactions, transfer, registerSecondSecret,
    registerSecondPublicKey, registerAsDelegate, upVote, downVote,
    registerMultiSignature, registerIpfs, multiPayment, delegateResignation,
    htlcSecret, htlcLock, htlcClaim, htlcRefund,
    entityRegister, entityUpdate, entityResign,
    nftRegisterCollection, nftCreate, nftTransfer, nftBurn
)

__all__ = [
    api, cfg, rest, crypto,
    hexlify, unhexlify, broadcastTransactions,
    transfer, registerSecondSecret, registerSecondPublicKey,
    registerAsDelegate, upVote, downVote, registerMultiSignature,
    registerIpfs, multiPayment, delegateResignation,
    htlcSecret, htlcLock, htlcClaim, htlcRefund,
    entityRegister, entityUpdate, entityResign,
    nftRegisterCollection, nftCreate, nftTransfer, nftBurn
]
