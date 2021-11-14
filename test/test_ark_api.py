# -*- coding: utf-8 -*-

import unittest
import dposlib
from dposlib import rest


def connection_enabled(func):
    def wrapper(*args, **kw):
        if rest.cfg.hotmode:
            return func(*args, **kw)
    return wrapper


class TestDposApi(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        # secrets used for testing
        self.secret = "secret"
        self.secondSecret = "secondSecret"
        # initialize on ark devnet
        if rest.use("dark"):
            self.wallet = dposlib.core.api.Wallet(
                dposlib.core.crypto.getAddress(
                    dposlib.core.crypto.getKeys(self.secret)["publicKey"]
                )
            )

    @connection_enabled
    def test_wallet(self):
        wlt = dposlib.core.api.Wallet(self.wallet.username)
        self.assertEqual(wlt.address, self.wallet.address)

    @connection_enabled
    def test_wallet_link(self):
        dposlib.core.api.link(self.wallet, self.secret, self.secondSecret)
        self.assertEqual(self.wallet._publicKey,
                         self.wallet.publicKey)
        self.assertEqual(self.wallet._secondPublicKey,
                         self.wallet.secondPublicKey)
