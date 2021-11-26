# -*- coding: utf-8 -*-

import base58
import json
from dposlib.util.bin import unhexlify, pack, pack_bytes


def compactJson(dic={}, **kw):
    return json.dumps(dict(dic, **kw), separators=(',', ':'), sort_keys=True)


def _9000_0(tx, buf):
    asset = tx["asset"].get("nftCollection", {})

    name = asset["name"]
    if 5 <= len(name) <= 40:
        pack("<B", buf, (len(name), ))
        pack_bytes(buf, name.encode("utf-8"))
    else:
        raise Exception("bad namelength [5-80]: %s" % name)

    description = asset["description"]
    if 5 <= len(description) <= 80:
        pack("<B", buf, (len(description), ))
        pack_bytes(buf, description.encode("utf-8"))
    else:
        raise Exception("bad description length [5-80]: %s" % description)

    pack("<I", buf, (max(1, asset["maximumSupply"]), ))

    jsonSchema = compactJson(asset["jsonSchema"])
    pack("<I", buf, (len(jsonSchema), ))
    pack_bytes(buf, jsonSchema.encode("utf-8"))

    allowedIssuers = asset.get("allowedIssuers", [])[:10]
    pack("<I", buf, (len(allowedIssuers), ))
    for allowedIssuer in allowedIssuers:
        pack_bytes(buf, unhexlify(allowedIssuer))

    metadata = compactJson(asset["metadata"])
    pack("<I", buf, (len(metadata), ))
    pack_bytes(buf, jsonSchema.encode("utf-8"))


def _9000_1(tx, buf):
    asset = tx["asset"].get("nftToken", {})

    pack_bytes(buf, unhexlify(asset["collectionId"]))

    attributes = compactJson(asset["attributes"])
    pack("<I", buf, (len(attributes), ))
    pack_bytes(buf, attributes.encode("utf-8"))

    recipientId = asset.get("recipientId", "")
    pack("<B", buf, (len(recipientId), ))
    if recipientId:
        pack_bytes(buf, recipientId.encode("utf-8"))


def _9000_2(tx, buf):
    asset = tx["asset"].get("nftTransfer", {})

    nftIds = asset["nftIds"][0:10]
    pack("<B", buf, (len(nftIds), ))
    for nftId in nftIds:
        pack_bytes(buf, unhexlify(nftId))

    recipientId = \
        str(tx["recipientId"]) \
        if not isinstance(tx["recipientId"], bytes) \
        else tx["recipientId"]
    recipientId = base58.b58decode_check(recipientId)
    pack_bytes(buf, recipientId)


def _9000_3(tx, buf):
    asset = tx["asset"].get("nftBurn", {})
    pack_bytes(buf, unhexlify(asset["nftId"]))


__all__ = [_9000_0, _9000_1, _9000_2, _9000_3]
