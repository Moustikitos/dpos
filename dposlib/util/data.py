# -*- coding: utf-8 -*-

import os
import io
import json

# from dposlib import PY3


def loadJson(path):
    """Load JSON data from path"""
    if os.path.exists(path):
        with io.open(path, encoding="utf-8") as in_:
            data = json.load(in_)
    else:
        data = {}
    try:
        in_.close()
        del in_
    except Exception:
        pass
    return data


def dumpJson(data, path):
    """Dump JSON data to path"""
    try:
        os.makedirs(os.path.dirname(path))
    except Exception:
        pass
    # with io.open(
    #     path, "w" if PY3 else "wb",
    #     **({"encoding": "utf-8"} if PY3 else {})
    # ) as out:
    with io.open(path, "w", encoding="utf-8") as out:
        json.dump(data, out, indent=4)
    try:
        out.close()
        del out
    except Exception:
        pass


def filter_dic(value):
    arktoshi = [
        "amount",
        "balance",
        "fee", "fees", "forged", "forgedRewards", "forgedFees",
        "reward", "rewards",
        "totalAmount", "totalFee", "totalForged", "total", "totalVotes",
        "unconfirmedBalance",
        "votes", "voteBalance"
    ]

    def cast_value(typ, v):
        try:
            return typ(v)/100000000.0
        except Exception:
            return filter_dic(v)

    if isinstance(value, dict):
        return dict(
            (
                k,
                cast_value(float, v) if k in arktoshi else
                filter_dic(v) if isinstance(v, dict) else
                v
            ) for k, v in value.items()
        )
    else:
        return value
