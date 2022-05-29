# -*- coding: utf-8 -*-
# © Toons

import sys
import hashlib
import json
from io import BytesIO

# all `v<x>.py` have to be imported here
from . import v2, v3

CACHE = {}


def serializePayload(tx):
    # compute a md5 hash over asset and amount
    asset = dict(tx.get("asset", {}))
    asset["amount"] = tx.get("amount", 0)
    asset["expiration"] = tx.get("expiration", 0)
    md5_asset = hashlib.md5(
        json.dumps(asset, sort_keys=True).encode("utf-8")
    ).hexdigest()
    # if hash already computed and nothing modified (asset or amount or
    # expiration) since
    if len(asset) and md5_asset == getattr(tx, "_assetHash", ""):
        return getattr(tx, "_serializedPayload")

    name = "_%(typeGroup)d_%(type)d" % tx
    key_name = "_%d" % tx["version"] + name
    func = CACHE.get(key_name, False)

    if func is False:
        # search decreasing versions
        for version in range(tx['version'], 1, -1):
            try:
                func = getattr(sys.modules[f"{__name__}.v{version}"], name)
            except AttributeError:
                pass
            else:
                CACHE[key_name] = func
                break
        # if nothing found:
        if key_name not in CACHE:
            raise NotImplementedError(
                "Unknown transaction %(typeGroup)d:%(type)d" % tx
            )

    buf = BytesIO()
    func(tx, buf)
    result = buf.getvalue()
    buf.close()

    setattr(tx, "_serializedPayload", result)
    setattr(tx, "_assetHash", md5_asset)
    return result
