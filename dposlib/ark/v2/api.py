# -*- coding: utf-8 -*-

import os
import getpass
import dposlib

from dposlib.util.data import filter_dic, dumpJson
from dposlib.ark.v2.mixin import loadPages, deltas
from dposlib.ark.tx import serialize
try:
    from dposlib.ark import ldgr
    LEDGERBLUE = True
except ImportError:
    LEDGERBLUE = False

deltas = deltas
GET = dposlib.rest.GET


class Wallet(dposlib.ark.Wallet):

    def __init__(self, address, **kw):
        dposlib.ark.Wallet.__init__(
            self, GET.api.wallets, address, **dict({"returnKey": "data"}, **kw)
        )

    @dposlib.ark.isLinked
    def sendIpfs(self, ipfs):
        "See [`dposlib.ark.v2.registerIpfs`](v2.md#registeripfs)."
        tx = dposlib.core.registerIpfs(ipfs)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @dposlib.ark.isLinked
    def multiSend(self, *pairs, **kwargs):
        "See [`dposlib.ark.v2.multiPayment`](v2.md#multipayment)."
        tx = dposlib.core.multiPayment(*pairs, **kwargs)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @dposlib.ark.isLinked
    def resignate(self):
        """
        See [`dposlib.ark.v2.delegateResignation`](v2.md#delegateresignation).
        """
        tx = dposlib.core.delegateResignation()
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @dposlib.ark.isLinked
    def sendHtlc(self, amount, address, secret,
                 expiration=24, vendorField=None):
        "See [`dposlib.ark.v2.htlcLock`](v2.md#htlclock)."
        tx = dposlib.core.htlcLock(
            amount, address, secret,
            expiration=expiration, vendorField=vendorField
        )
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @dposlib.ark.isLinked
    def claimHtlc(self, txid, secret):
        "See [`dposlib.ark.v2.htlcClaim`](v2.md#htlcclaim)."
        tx = dposlib.core.htlcClaim(txid, secret)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @dposlib.ark.isLinked
    def refundHtlc(self, txid):
        "See [`dposlib.ark.v2.htlcRefund`](v2.md#htlcrefund)."
        tx = dposlib.core.htlcRefund(txid)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))


if LEDGERBLUE:

    class Ledger(Wallet):
        """
        Ledger wallet api.
        """

        def __init__(self, account, index, network=0, **kw):
            self._debug = kw.pop("debug", False)
            self._schnorr = kw.pop("schnorr", True)
            # aip20 : https://github.com/ArkEcosystem/AIPs/issues/29
            self._derivationPath = "44'/%s'/%s'/%s/%s" % (
                getattr(dposlib.rest.cfg, "slip44", "111"),
                getattr(dposlib.rest.cfg, "aip20", network),
                account,
                index
            )
            self._dongle_path = ldgr.parseBip44Path(self._derivationPath)
            puk = ldgr.sendApdu(
                [ldgr.buildPukApdu(self._dongle_path)], debug=self._debug
            )[2:]
            object.__setattr__(self, "publicKey", puk)
            object.__setattr__(
                self, "address", dposlib.core.crypto.getAddress(puk)
            )
            Wallet.__init__(self, self.address, **kw)

        @staticmethod
        def fromDerivationPath(derivationPath, **kw):
            ldgr_wlt = Ledger(0, 0, 0, **kw)
            ldgr_wlt._derivationPath = derivationPath
            ldgr_wlt._dongle_path = ldgr.parseBip44Path(derivationPath)
            puk = ldgr.sendApdu(
                [ldgr.buildPukApdu(ldgr_wlt._dongle_path)],
                debug=ldgr_wlt._debug
            )[2:]
            object.__setattr__(ldgr_wlt, "publicKey", puk)
            object.__setattr__(
                ldgr_wlt, "address", dposlib.core.crypto.getAddress(puk)
            )
            ldgr_wlt._Content__args = (ldgr_wlt.address,)
            ldgr_wlt.update()
            return ldgr_wlt

        def _finalizeTx(self, tx):
            if "fee" not in tx or self._fee is not None:
                tx.fee = self._fee
            tx.feeIncluded = self._fee_included
            tx["senderPublicKey"] = self.publicKey
            tx["signature"] = ldgr.sendApdu(
                ldgr.buildSignatureApdu(
                    serialize(tx),
                    self._dongle_path,
                    "tx",
                    self._schnorr
                ),
                debug=self._debug
            )

            if tx._secondPublicKey is not None:
                try:
                    k2 = dposlib.core.crypto.getKeys(
                        getpass.getpass("second secret > ")
                    )
                    while k2.get("publicKey", None) != tx._secondPublicKey:
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


class Delegate(dposlib.ark.Content):

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
        dposlib.ark.Content.__init__(
            self, GET.api.delegates, username,
            **dict({"returnKey": "data"}, **kw)
        )

    def getRecentBlocks(self, limit=50):
        return loadPages(
            GET.api.delegates.__getattr__(self.username).blocks,
            limit=limit
        )


class Block(dposlib.ark.Content):

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
        dposlib.ark.Content.__init__(
            self, GET.api.blocks, blk_id, **dict({"returnKey": "data"}, **kw)
        )


# TODO: redefine
class Webhook(dposlib.ark.Content):

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
        dposlib.ark.Content.__init__(
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
