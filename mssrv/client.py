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
def putSignature(network, publicKey, txid, ms_publicKey, signature):
    return rest.PUT.multisignature.__getattr__(network).put.__getattr__(
        publicKey
    )(
        peer=API_PEER,
        info={"publicKey": ms_publicKey, "signature": signature, "id": txid}
    )


def remoteSignWithSecret(network, publicKey, txid, secret=None):
    return remoteSignWithKey(
        network, publicKey, txid,
        hexlify(
            secp256k1.hash_sha256(
                secret if secret is not None else
                getpass.getpass("secret > ")
            )
        )
    )


def remoteSignWithKey(network, publicKey, txid, ms_privateKey):
    ms_publicKey = hexlify(
        secp256k1.PublicKey.from_seed(unhexlify(ms_privateKey)).encode()
    )

    wallet = getWallet(network, publicKey).get("data", {})
    if txid in wallet:
        return putSignature(
            network, publicKey, txid, ms_publicKey,
            crypto.getSignatureFromBytes(
                crypto.getBytes(
                    wallet[txid],
                    exclude_sig=True,
                    exclude_multi_sig=True,
                    exclude_second_sig=True
                ),
                ms_privateKey
            )
        )
    else:
        raise Exception("%s transaction not found" % txid)
