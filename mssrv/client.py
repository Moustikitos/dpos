# -*- coding:utf-8 -*-
# (C) Toons MIT Licence

import getpass
from dposlib import rest
from dposlib.ark import secp256k1, crypto
from dposlib.util.bin import hexlify, unhexlify

API_PEER = "http://musig.arky-delegate.info"


def getAll(network):
    return rest.GET.multisignature.__getattr__(network).get(peer=API_PEER)


def getWallet(network, publicKey):
    return rest.GET.multisignature.__getattr__(network).__getattr__(publicKey)(
        peer=API_PEER
    )


def postNewTransactions(network, *tx):
    return rest.POST.multisignature.__getattr__(network).post(
        peer=API_PEER,
        transactions=tx
    )


def putSignature(network, txid, publicKey, signature):
    return rest.PUT.multisignature.__getattr__(network).__getattr__(txid).put(
        peer=API_PEER,
        pair={"publicKey":publicKey, "signature":signature}
    )


def remoteSignWithSecret(network, txid, secret=None):
    return remoteSignWithKey(
        network, txid,
        hexlify(
            secp256k1.hash_sha256(
                secret if secret is not None else 
                getpass.getpass("secret > ")
            )
        )
    )


def remoteSignWithKey(network, txid, privateKey):
    publicKey = hexlify(
        secp256k1.PublicKey.from_seed(unexlify(privateKey)).encode()
    )

    wallet = getWallet(network, publicKey)
    if txid in wallet:
        return putSignature(
            network, txid, publicKey,
            crypto.getSignatureFromBytes(
                crypto.getBytes(
                    wallet[txid],
                    exclude_sig=True,
                    exclude_multi_sig=True,
                    exclude_second_sig=True
                ),
                privateKey
            )
        )
    else:
        raise Exception("%s transaction not found" % txid)