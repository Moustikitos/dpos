# -*- coding: utf-8 -*-
# © Toons

import sys
import hashlib
import json
from io import BytesIO

from . import v2, v3

CACHE = {}


def serializePayload(tx):
    asset = tx.get("asset", {})
    md5_asset = hashlib.md5(
        json.dumps(asset, sort_keys=True).encode("utf-8")
    ).hexdigest()

    # if hash already computed and nothing modified since
    if len(asset) and md5_asset == getattr(tx, "_assetHash", ""):
        return getattr(tx, "_serializedPayload")

    name = "_%(typeGroup)d_%(type)d" % tx
    func = CACHE.get(name, False)

    if func is False:
        # search
        for version in range(tx['version'], 1, -1):
            try:
                func = getattr(sys.modules[f"{__name__}.v{version}"], name)
            except AttributeError:
                pass
            else:
                CACHE[name] = func
                break
        if name not in CACHE:
            raise Exception("Unknown transaction %(typeGroup)d:%(type)d" % tx)

    buf = BytesIO()
    func(tx, buf)
    result = buf.getvalue()
    buf.close()

    setattr(tx, "_serializedPayload", result)
    setattr(tx, "_assetHash", md5_asset)
    return result
