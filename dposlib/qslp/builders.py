# -*- coding: utf-8 -*-

"""
QSLP transaction builders. See [QSLP API](https://aslp.qredit.dev) for more
information.

  - QSLP1 token is an ERC20-equivalent-smartbridge-embeded token.
  - QSLP2 token is an NFT-equivalent-smartbridge-embeded token.

```python
>>> t = dposlib.core.qslpGenesis(
...    2, "TTK", "Toon's token", 250000,
...    du="ipfs://bafkreigfxalrf52xm5ecn4lorfhiocw4x5cxpktnkiq3atq6jp2elktobq",
...    no="For testing purpose only.", pa=True, mi=True
... )
>>> t.vendorField
'{"aslp1":{"tp":"GENESIS","de":"2","sy":"TTK","na":"Toon\'s token","qt":"25000\
000","du":"ipfs://bafkreigfxalrf52xm5ecn4lorfhiocw4x5cxpktnkiq3atq6jp2elktobq"\
,"no":"For testing purpose only."}}'
>>>
```
"""

import json

from dposlib import cfg
from dposlib.ark.tx import Transaction
from dposlib.qslp.api import GET


def qslpGenesis(de, sy, na, qt, du=None, no=None, pa=False, mi=False):
    """
    Build a QSLP1 genesis transaction.

    Args:
        de (int): decimal number.
        sy (str): token symbol.
        na (str): token name.
        qt (int): maximum supply.
        du (str): document URI.
        no (str): token notes.
        pa (bool): pausable token ?
        mi (bool): mintable token ?

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction with appropriate QSLP1
            `vendorField`.
    """
    args = dict(decimals=de, symbol=sy, name=na, quantity=qt)
    if du:
        args["uri"] = du
    if no:
        args["notes"] = no[:32]
    if pa:
        args["pausable"] = "true"
    if mi:
        args["mintable"] = "true"

    smartbridge = GET.api.vendor_aslp1_genesis(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=100000000,
        recipientId=cfg.master_address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslpBurn(tkid, qt, no=None):
    """
    Build a QSLP1 burn transaction.

    Args:
        tkid (str): token id.
        qt (int): quantity to burn.
        no (str): token notes.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction with appropriate QSLP1
            `vendorField`.
    """
    args = dict(tokenid=tkid, quantity=qt)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp1_burn(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=cfg.master_address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslpMint(tkid, qt, no=None):
    """
    Build a QSLP1 mint transaction.

    Args:
        tkid (str): token id.
        qt (int): quantity to burn.
        no (str): token notes.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction with appropriate QSLP1
            `vendorField`.
    """
    args = dict(tokenid=tkid, quantity=qt)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp1_mint(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=cfg.master_address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslpSend(address, tkid, qt, no=None):
    """
    Build a QSLP1 send transaction.

    Args:
        address (str): recipient wallet address.
        tkid (str): token id.
        qt (int): quantity to burn.
        no (str): token notes.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction with appropriate QSLP1
            `vendorField`.
    """
    args = dict(tokenid=tkid, quantity=qt)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp1_send(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslpPause(tkid, no=None):
    """
    Build a QSLP1 pause transaction.

    Args:
        tkid (str): token id.
        no (str): token notes.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction with appropriate QSLP1
            `vendorField`.
    """
    args = dict(tokenid=tkid)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp1_pause(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=cfg.master_address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslpResume(tkid, no=None):
    """
    Build a QSLP1 resume transaction.

    Args:
        tkid (str): token id.
        no (str): token notes.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction with appropriate QSLP1
            `vendorField`.
    """
    args = dict(tokenid=tkid)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp1_resume(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=cfg.master_address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslpNewOwner(address, tkid, no=None):
    """
    Build a QSLP1 owner change transaction.

    Args:
        address (str): new owner wallet address.
        tkid (str): token id.
        no (str): token notes.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction with appropriate QSLP1
            `vendorField`.
    """
    args = dict(tokenid=tkid)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp1_newowner(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslpFreeze(address, tkid, no=None):
    """
    Build a QSLP1 freeze transaction.

    Args:
        address (str): frozen wallet address.
        tkid (str): token id.
        no (str): token notes.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction with appropriate QSLP1
            `vendorField`.
    """
    args = dict(tokenid=tkid)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp1_freeze(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslpUnFreeze(address, tkid, no=None):
    """
    Build a QSLP1 unfreeze transaction.

    Args:
        address (str): unfrozen wallet address.
        tkid (str): token id.
        no (str): token notes.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction with appropriate QSLP1
            `vendorField`.
    """
    args = dict(tokenid=tkid)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp1_unfreeze(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslp2Genesis(sy, na, du=None, no=None, pa=False):
    """
    Build a QSLP2 genesis transaction.

    Args:
        sy (str): token symbol.
        na (str): token name.
        du (str): URI.
        no (str): token notes.
        pa (bool): pausable token ?

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction with appropriate QSLP2
            `vendorField`.
    """
    args = dict(symbol=sy, name=na)
    if du:
        args["uri"] = du
    if no:
        args["notes"] = no[:32]
    if pa:
        args["pausable"] = "true"

    smartbridge = GET.api.vendor_aslp2_genesis(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=100000000,
        recipientId=cfg.master_address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslp2Pause(tkid, no=None):
    """
    Build a QSLP2 pause transaction.

    Args:
        tkid (str): token id.
        no (str): token notes.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction with appropriate QSLP2
            `vendorField`.
    """
    args = dict(tokenid=tkid)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp2_pause(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=cfg.master_address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslp2Resume(tkid, no=None):
    """
    Build a QSLP2 resume transaction.

    Args:
        tkid (str): token id.
        no (str): token notes.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction with appropriate QSLP2
            `vendorField`.
    """
    args = dict(tokenid=tkid)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp2_resume(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=cfg.master_address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslp2NewOwner(address, tkid, no=None):
    """
    Build a QSLP2 owner change transaction.

    Args:
        address (str): new owner wallet address.
        tkid (str): token id.
        no (str): token notes.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction with appropriate QSLP2
            `vendorField`.
    """
    args = dict(tokenid=tkid)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp2_newowner(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslp2AuthMeta(address, tkid, no=None):
    """
    Build a QSLP2 meta change authorization transaction.

    Args:
        address (str): authorized wallet address.
        tkid (str): token id.
        no (str): token notes.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction with appropriate QSLP2
            `vendorField`.
    """
    args = dict(tokenid=tkid)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp2_authmeta(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslp2RevokeMeta(address, tkid, no=None):
    """
    Build a QSLP2 meta change revokation transaction.

    Args:
        address (str): revoked wallet address.
        tkid (str): token id.
        no (str): token notes.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction with appropriate QSLP2
            `vendorField`.
    """
    args = dict(tokenid=tkid)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp2_revokemeta(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslp2Clone(tkid, no=None):
    """
    Build a QSLP2 clone transaction.

    Args:
        tkid (str): token id.
        no (str): token notes.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction with appropriate QSLP2
            `vendorField`.
    """
    args = dict(tokenid=tkid)
    if no:
        args["notes"] = no[:32]

    smartbridge = GET.api.vendor_aslp2_clone(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=cfg.master_address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslp2AddMeta(tkid, na, dt, ch=None):
    """
    Build a QSLP2 metadata edition transaction.

    Args:
        tkid (str): token id.
        na (str): name of the metadata info.
        dt (str): data of metadata.
        ch (int): chunk number.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction with appropriate QSLP2
            `vendorField`.
    """
    args = dict(tokenid=tkid, name=na, data=dt)
    if ch:
        args["chunk"] = ch

    smartbridge = GET.api.vendor_aslp2_addmeta(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=cfg.master_address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


def qslp2VoidMeta(tkid, tx):
    """
    Build a QSLP2 metadata cleaning transaction.

    Args:
        tkid (str): token id.
        tx (str): transaction id of metadata to void.

    Returns:
        dposlib.ark.tx.Transaction: orphan transaction with appropriate QSLP2
            `vendorField`.
    """
    args = dict(tokenid=tkid, txid=tx)

    smartbridge = GET.api.vendor_aslp2_voidmeta(**args)
    if smartbridge.pop("status", 0) != 200:
        raise Exception(smartbridge.get("error", "QSLP smartbridge error"))

    return Transaction(
        typeGroup=1,
        type=0,
        amount=1,
        recipientId=cfg.master_address,
        vendorField=json.dumps(smartbridge, separators=(",", ":"))
    )


__all__ = [
    qslpGenesis, qslpBurn, qslpMint, qslpSend, qslpPause, qslpResume,
    qslpNewOwner, qslpFreeze, qslpUnFreeze,
    qslp2Genesis, qslp2Pause, qslp2Resume,
    qslp2NewOwner, qslp2AuthMeta, qslp2RevokeMeta,
    qslp2Clone, qslp2AddMeta, qslp2VoidMeta
]
