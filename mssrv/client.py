# -*- coding:utf-8 -*-
# (C) Toons MIT Licence

import getpass
from dposlib import rest
from dposlib.ark import secp256k1, crypto
from dposlib.util.bin import hexlify, unhexlify

API_PEER = None


def peer_available(func):
    def wrapper(*args, **kw):
        if rest.checkLatency(API_PEER):
            return func(*args, **kw)
        else:
            raise Exception("peer not available")
    return wrapper


@peer_available
def getAll(network):
    return rest.GET.multisignature.__getattr__(network).get(peer=API_PEER)


@peer_available
def getWallet(network, publicKey):
    return rest.GET.multisignature.__getattr__(network).__getattr__(publicKey)(
        peer=API_PEER
    )


@peer_available
def postNewTransactions(network, *tx):
    return rest.POST.multisignature.__getattr__(network).post(
        peer=API_PEER,
        transactions=tx
    )


@peer_available
def putSignature(network, ms_publicKey, txid, publicKey, signature):
    return rest.PUT.multisignature.__getattr__(network).__getattr__(
        ms_publicKey
    ).put(
        peer=API_PEER,
        info={"publicKey": publicKey, "signature": signature, "id": txid}
    )


def remoteSignWithSecret(network, ms_publicKey, txid, secret=None):
    return remoteSignWithKey(
        network, ms_publicKey, txid,
        hexlify(
            secp256k1.hash_sha256(
                secret if secret is not None else
                getpass.getpass("secret > ")
            )
        )
    )


def remoteSignWithKey(network, ms_publicKey, txid, privateKey):
    publicKey = hexlify(
        secp256k1.PublicKey.from_seed(unhexlify(privateKey)).encode()
    )

    wallet = getWallet(network, ms_publicKey).get("data", {})
    if txid in wallet:
        options = {} if wallet[txid]["type"] == 4 else {
            "exclude_sig": True,
            "exclude_multi_sig": True,
            "exclude_second_sig": True
        }
        return putSignature(
            network, ms_publicKey, txid, publicKey,
            crypto.getSignatureFromBytes(
                crypto.getBytes(wallet[txid], **options),
                privateKey
            )
        )
    else:
        raise Exception("%s transaction not found" % txid)
