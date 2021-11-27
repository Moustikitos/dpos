# -*- coding: utf-8 -*-

from dposlib.ark.tx import Transaction


def nftRegisterCollection(name, desc, supply, schema, *issuers, **meta):
    """
    Build a NFT collection registration transaction.

    Args:
        name (str): NFT name.
        desc (str): NFT description.
        supply (int): NFT maximum supply.
        schema (dict): NFT json schema.
        issuers (*args): list of public keys allowed to issue the NFT.
        meta (**kwargs): NFT metadata.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction.
    """
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


def nftCreate(collectionId, attributes, address=None):
    """
    Build a NFT mint transaction.

    Args:
        collectionId (str): NFT collection id.
        attributes (dict): NFT attributes matching defined schema.
        address (str): recipient address.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction.
    """
    asset = {
        "nftToken": {
            "collectionId": collectionId,
            "attributes": dict(attributes)
        }
    }

    if address is not None:
        asset["nftToken"]["recipientId"] = address

    return Transaction(typeGroup=9000, type=1, asset=asset)


def nftTransfer(address, *ids):
    """
    Build a NFT transfer transaction.

    Args:
        address (str): recipient address.
        ids (list): list of NFT id to send (maximum=10).

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction.
    """
    return Transaction(
        typeGroup=9000, type=2,
        asset={
            "nftTransfer": {
                "nftIds": ids[:10],
                "recipientId": address,
            }
        }
    )


def nftBurn(txid):
    """
    Build a NFT burn transaction.

    Args:
        txid (str): NFT mint transaction id.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction.
    """
    return Transaction(
        typeGroup=9000, type=3,
        asset={"nftBurn": {"nftId": txid}}
    )


__all__ = [nftRegisterCollection, nftCreate, nftTransfer, nftBurn]
