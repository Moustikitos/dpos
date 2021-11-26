# -*- coding: utf-8 -*-

from dposlib.ark.tx import Transaction


def NftRegisterCollection(name, desc, supply, schema, *issuers, **meta):
    asset = {
        "nftCollection": {
            "name": name,
            "description": desc,
            "maximumSupply": min(1, supply),
            "jsonSchema": dict(schema)
        }
    }

    if meta:
        asset["nftCollection"]["metadata"] = meta

    if issuers:
        asset["nftCollection"]["allowedIssuers"] = list(issuers)

    return Transaction(typeGroup=9000, type=0, asset=asset)


def NftCreate(collectionId, attributes, address=None):
    asset = {
        "nftToken": {
            "collectionId": collectionId,
            "attributes": dict(attributes)
        }
    }

    if address is not None:
        asset["nftToken"]["recipientId"] = address

    return Transaction(typeGroup=9000, type=1, asset=asset)


def NftTransfer(address, *ids):
    return Transaction(
        typeGroup=9000, type=2,
        asset={
            "nftTransfer": {
                "nftIds": ids[:10],
                "recipientId": address,
            }
        }
    )


def NftBurn(txid):
    return Transaction(
        typeGroup=9000, type=3,
        asset={"nftBurn": {"nftId": txid}}
    )


__all__ = [NftRegisterCollection, NftCreate, NftTransfer, NftBurn]
