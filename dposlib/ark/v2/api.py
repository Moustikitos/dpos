# -*- coding: utf-8 -*-
# © Toons
# ~ https://docs.ark.io/api/public/v2/

import os
import getpass
import dposlib

from dposlib.util.data import filter_dic, dumpJson
from dposlib.ark.v2.mixin import loadPages, deltas
try:
    from dposlib.ark import ldgr
    LEDGERBLUE = True
except ImportError:
    LEDGERBLUE = False

deltas = deltas
GET = dposlib.rest.GET


class Wallet(dposlib.blockchain.Wallet):
    # TODO: set delegate property
    # TODO: add transactions 5 - 10
    
    def __init__(self, address, **kw):
        dposlib.blockchain.Data.__init__(
            self, GET.api.wallets, address, **dict({"returnKey": "data"}, **kw)
        )

    def getDelegate(self):
        return Delegate(self.username) if self.isDelegate else None

    def transactions(self, limit=50):
        sent = loadPages(
            GET.api.wallets.__getattr__(self.address).transactions.sent,
            limit=limit
        )
        received = loadPages(
            GET.api.wallets.__getattr__(self.address).transactions.received,
            limit=limit
        )
        return [
            filter_dic(dic) for dic in sorted(
                received+sent,
                key=lambda e: e.get("timestamp", {}).get("epoch"),
                reverse=True
            )
        ][:limit]


if LEDGERBLUE:
    class NanoS(Wallet):

        def __init__(self, account, index, network=1, **kw):
            # aip20 : https://github.com/ArkEcosystem/AIPs/issues/29
            self.derivationPath = "44'/%s'/%s'/%s'/%s" % (
                dposlib.rest.cfg.slip44,
                getattr(dposlib.rest.cfg, "aip20", network),
                account,
                index
            )
            self.address = dposlib.core.crypto.getAddress(
                ldgr.getPublicKey(ldgr.parseBip32Path(self.derivationPath))
            )
            self.debug = kw.pop("debug", False)
            Wallet.__init__(self, self.address, **kw)

        @staticmethod
        def fromDerivationPath(derivationPath, **kw):
            nanos = NanoS(0, 0, 0, **kw)
            address = dposlib.core.crypto.getAddress(
                ldgr.getPublicKey(ldgr.parseBip32Path(derivationPath))
            )
            nanos.address = address
            nanos.derivationPath = derivationPath
            nanos._Data__args = (address,)
            nanos.update()
            return nanos

        def _finalizeTx(self, tx, fee=None, fee_included=False):
            if "fee" not in tx or fee is not None:
                tx.setFees(fee)
            tx.feeIncluded() if fee_included else tx.feeExcluded()

            tx["senderId"] = self.address
            if tx["type"] in [1, 3, 4] and "recipientId" not in tx:
                tx["recipientId"] = self.address

            try:
                ldgr.signTransaction(tx, self.derivationPath, self.debug)
            except ldgr.ledgerblue.commException.CommException:
                raise Exception("transaction cancelled")

            if self.secondPublicKey is not None:
                try:
                    k2 = dposlib.core.crypto.getKeys(
                        getpass.getpass("second secret > ")
                    )
                    while k2.get("publicKey", None) != self.secondPublicKey:
                        k2 = dposlib.core.crypto.getKeys(
                            getpass.getpass("second secret > ")
                        )
                except KeyboardInterrupt:
                    raise Exception("transaction cancelled")
                else:
                    tx["signSignature"] = dposlib.core.crypto.getSignature(
                        tx, k2["privateKey"]
                    )

            tx.identify()
            return tx


class Delegate(dposlib.blockchain.Data):

    wallet = property(lambda cls: Wallet(cls.address), None, None, "")
    voters = property(
        lambda cls: list(sorted(
            [
                filter_dic(dic) for dic in
                loadPages(GET.api.delegates.__getattr__(cls.username).voters)
            ],
            key=lambda e: e["balance"],
            reverse=True
        )),
        None, None, ""
    )
    lastBlock = property(
        lambda cls: Block(cls.blocks["last"]["id"]), None, None, ""
    )

    def __init__(self, username, **kw):
        dposlib.blockchain.Data.__init__(
            self, GET.api.delegates, username,
            **dict({"returnKey": "data"}, **kw)
        )

    def getRecentBlocks(self, limit=50):
        return loadPages(
            GET.api.delegates.__getattr__(self.username).blocks,
            limit=limit
        )


class Block(dposlib.blockchain.Data):

    previous = property(
        lambda cls: Block(cls._Data__dict["previous"]),
        None, None, ""
    )

    transactions = property(
        lambda cls: [
            filter_dic(dic) for dic in loadPages(
                GET.api.blocks.__getattr__(cls.id).transactions,
                limit=False
            )
        ], None, None, ""
    )

    def __init__(self, blk_id, **kw):
        dposlib.blockchain.Data.__init__(
            self, GET.api.blocks, blk_id, **dict({"returnKey": "data"}, **kw)
        )


class Webhook(dposlib.blockchain.Data):

    @staticmethod
    def create(peer, event, target, conditions):
        data = dposlib.rest.POST.api.webhooks(
            peer=peer, event=event, target=target, conditions=conditions,
            returnKey="data"
        )
        if "token" in data:
            dumpJson(data, os.path.join(
                dposlib.ROOT,
                ".webhooks",
                dposlib.rest.cfg.network, data["token"][32:]
            ))
        return Webhook(data["id"], peer=peer)

    def __init__(self, whk_id, **kw):
        dposlib.blockchain.Data.__init__(
            self, GET.api.webhooks, "%s" % whk_id,
            **dict({"track": False, "returnKey": "data"}, **kw)
        )

    def delete(self):
        dposlib.rest.DELETE.api.webhooks(
            "%s" % self.id, peer=self.__kwargs.get("peer", None)
        )
        whk_path = os.path.join(
            dposlib.ROOT, ".webhooks", dposlib.rest.cfg.network,
            self.token[32:]
        )
        if os.path.exists(whk_path):
            os.remove(whk_path)
