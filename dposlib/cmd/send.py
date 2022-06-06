# -*- coding:utf-8 -*-

import sys
import argparse

import dposlib
from dposlib import rest
from dposlib.ark import api

builders = {
    "send": "transfer",
    "vote": "upVote",
    "lock": "htlcLock",
    "claim": "htlcClaim",
    "burn": "burn"
}

arg_types = {
    "transfer": (float, str, str, float),
    "upVote": (str, ),
    "htlcLock": (float, str, str, float, str, int),
    "htlcClaim": (str, str, int),
    "burn": (float, str)
}

parser = argparse.ArgumentParser()
parser.add_argument("net")
parser.add_argument("action")
parser.add_argument("args", nargs="*")
parser.add_argument("-i", "--identity", required=True)
parser.add_argument("--vendor-field", default=None, dest="vendorField")


def main():
    args = parser.parse_args(sys.argv[1:])
    rest.use(args.net, cold_start=True)

    builder_name = builders[args.action]
    assert builder_name in arg_types, \
        "%s builder not implemented" % builder_name
    builder_types = arg_types[builder_name]
    builder = getattr(dposlib.core, builder_name)

    # get identity info from bockchain if provided
    wallet = api.Wallet(args.identity)
    assert hasattr(wallet, "address"), \
        "identity %s not found in blockchain" % args.identity

    # build the transaction ---------------------------------------------------
    params = []
    try:
        for i in range(len(args.args)):
            params.append(builder_types[i](args.args[i]))
        tx = builder(*params)
    except Exception as error:
        print("Error occured on transaction build... Check command line args.")
        print(builder.__doc__)
        print("%r" % error)
        sys.exit(1)
    # if vote transaction apply switch vote transformation
    if args.action == "vote":
        tx.senderPublicKey = wallet.publicKey
        dposlib.core.switchVote(tx)
    # update the vendor field f asked
    if args.vendorField is not None:
        tx.vendorField = args.vendorField

    # sign the transaction ----------------------------------------------------
    wallet.link()
    if wallet._isLinked and not hasattr(wallet, "publicKey"):
        object.__setattr__(
            wallet, "publicKey", dposlib.core.crypto.getKeys(
                wallet._privateKey
            )["publicKey"]
        )
    tx.signWithKeys(wallet.publicKey, wallet._privateKey)
    if hasattr(wallet, "_secondPrivateKey"):
        tx.signSignWithKey(wallet._secondPrivateKey)
    tx.identify()

    # broadcast transaction ---------------------------------------------------
    print("%r" % tx)
    if input("Do you want to broadcast ? [y/n]> ").lower() == "y":
        print(dposlib.core.broadcastTransactions(tx))


if __name__ == "__main__":
    sys.exit(main())
