# -*- coding:utf-8 -*-

import re
import sys
import argparse

import dposlib
from dposlib import rest, net
from dposlib.ark import api

builders = {
    "fund": "transfer",
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

networks = [n for n in dir(net) if n[0] != '_']
parser = argparse.ArgumentParser(description="Command line wallet.")
parser.add_argument("net", help=f"any of [{', '.join(networks)}]")
parser.add_argument("action", help=f"any of [{', '.join(builders.keys())}]")
parser.add_argument("args", nargs="*", help="arguments to be passed to transaction builder")
parser.add_argument("-i", "--identity", help="public key, wallet address or delegate username", required=True)
parser.add_argument("-f", "--fee", default="avg", help="transaction fee", dest="fee")
parser.add_argument("--vendor-field", default=None, dest="vendorField")


def main():
    args = parser.parse_args(sys.argv[1:])
    rest.use(args.net, cold_start=True)

    if args.action not in builders:
        print("unknown action %s" % args.action)
        return 1
    elif builders[args.action] not in arg_types:
        print("%s builder not implemented" % builders[args.action])
        return 1

    builder_name = builders[args.action]
    builder_types = arg_types[builder_name]
    if args.net not in ["tsxp"]:
        if builder_name == "transfer":
            builder_name = "legacyTransfer"
        if builder_name == "upVote":
            builder_name = "legacyVote"
    builder = getattr(dposlib.core, builder_name)

    # fee management
    if args.fee in ["min", "avg", "max"]:
        fee = args.fee
    elif re.match("^[0-9]+.[0-9]+$", args.fee):
        fee = int(float(args.fee) * 100000000)
    elif re.match("^x[1-9][0-9]{3,6}$", args.fee):
        if not (1000 <= int(args.fee[1:]) <= 1000000):
            print("Fee multiplier shoud be >= 1000 and <= 1000000")
            return 1
        fee = args.fee[1:]
    else:
        print("Error occured on fee computation...")
        return 1

    if re.match("^ldgr:([0-9]+);([0-9]+)$", args.identity):
        accnt, idx = [int(e) for e in args.identity.split(":")[-1].split(";")]
        try:
            assert "sxp" not in args.net, "Solar network not supported"
            wallet = api.Ledger(account=accnt, index=idx, fee=fee, debug=True)
        except Exception as error:
            print("%r" % error)
            return 1
    else:
        # get identity info from bockchain if provided
        wallet = api.Wallet(args.identity, fee=args.fee)
        print("Enter %s credentials:" % args.identity)
        wallet.link()

    if not hasattr(wallet, "address"):
        print("identity %s not found in blockchain" % args.identity)
        return 1

    # build the transaction ---------------------------------------------------
    params = []
    try:
        for i in range(len(args.args)):
            params.append(builder_types[i](args.args[i]))
        if args.action == "vote" and args.net in ["tsxp"]:
            if "=" in params[0]:
                pairs = [elem.split("=") for elem in params[0].split(",")]
                tx = builder(**dict([p[0], float(p[1])] for p in pairs))
            else:
                tx = builder(*params[0].split(","))
        else:
            tx = builder(*params)
    except Exception as error:
        print("Error occured on transaction build... Check command line args.")
        print(builder.__doc__)
        print("%r" % error)
        return 1

    # if legacyVote transaction apply switch vote transformation
    if tx["type"] == 3 and tx["typeGroup"] == 1:
        tx.senderPublicKey = wallet.publicKey
        tx = getattr(dposlib.core, "switchVote")(tx)

    # update the vendor field f asked
    if args.vendorField is not None:
        tx.vendorField = args.vendorField

    # sign the transaction ----------------------------------------------------
    if getattr(wallet, "_isLinked", False):
        # for uncreated wallet
        if not hasattr(wallet, "publicKey"):
            object.__setattr__(
                wallet, "publicKey", dposlib.core.crypto.getKeys(
                    wallet._privateKey
                )["publicKey"]
            )
    elif isinstance(wallet, api.Ledger):
        print("Validate the transaction with your ledger...")
    else:
        return 1

    try:
        wallet._finalizeTx(tx)
    except Exception as error:
        print("Error occured during transaction signature...")
        print("%r" % error)
        return 1

    if tx.get("signature", None) in ["", None]:
        print("Ledger app failed to issue signature")
        return 1

    # broadcast transaction ---------------------------------------------------
    print("%r" % tx)
    if input("Do you want to broadcast ? [y/n]> ").lower() == "y":
        print(dposlib.core.broadcastTransactions(tx))
        return 0
    else:
        print("Transaction canceled !")
        return 1


if __name__ == "__main__":
    sys.exit(main())
