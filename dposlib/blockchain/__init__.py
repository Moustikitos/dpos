# -*- coding: utf-8 -*-
# © Toons

"""
:mod:`dposlib.blockchain` package provides :class:`Transaction` and
:class:`Wallet` classes.

A blockchain have to be loaded first to use :class:`Transaction`:

>>> from dposlib import blockchain
>>> tx = blockchain.Transaction(amount=1, recipientId="D7seWn8JLVwX4nHd9hh2Lf7\
gvZNiRJ7qLk", version=1)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:/Users/Bruno/Python/../GitHub/dpos/dposlib/blockchain/__init__.py", \
line 156, in __init__
    raise Exception("no blockchain loaded")
Exception: no blockchain loaded
>>> from dposlib import rest
>>> rest.use("d.ark")
True
>>> tx = blockchain.Transaction(amount=1, recipientId="D7seWn8JLVwX4nHd9hh2Lf7\
gvZNiRJ7qLk", version=1)
>>> tx.amount
1
"""

import sys
import json
import weakref
import getpass

from collections import OrderedDict

import dposlib
import dposlib.rest
from dposlib.blockchain import slots
from dposlib.util.asynch import setInterval


def track_data(value=True):
    Data.TRACK = value


def _unlink(cls):
    """
    Remove public and private keys.
    """
    for attr in [
        '_privateKey',
        '_publicKey',
        '_secondPublicKey',
        '_secondPrivateKey'
    ]:
        if hasattr(cls, attr):
            delattr(cls, attr)


# API
class Data:

    REF = set()
    EVENT = False
    TRACK = True

    datetime = property(
        lambda cls: slots.getRealTime(cls.timestamp["epoch"]),
        None, None, ""
    )

    def unlink(self):
        _unlink(self)

    @staticmethod
    def wallet_islinked(func):
        def wrapper(*args, **kw):
            obj = args[0]
            if hasattr(obj, "derivationPath"):
                return func(*args, **kw)
            elif not hasattr(obj, "address"):
                raise Exception("not a wallet")
            elif (
                obj.publicKey is None and
                dposlib.core.crypto.getAddress(
                    getattr(obj, "_publicKey", " ")
                ) == obj.address
            ) or (
                getattr(obj, "_publicKey", None) == obj.publicKey and
                getattr(obj, "_secondPublicKey", None) == getattr(
                    obj, "secondPublicKey", None
                )
            ):
                return func(*args, **kw)
            else:
                raise Exception("wallet not linked yet")
        return wrapper

    @setInterval(30)
    def heartbeat(self):
        dead = set()
        for ref in list(Data.REF):
            obj = ref()
            if obj:
                obj.update()
            else:
                dead.add(ref)
        Data.REF -= dead

        if len(Data.REF) == 0:
            Data.EVENT.set()
            Data.EVENT = False

    def __init__(self, endpoint, *args, **kwargs):
        track = kwargs.pop("track", Data.TRACK)
        self.__endpoint = endpoint
        self.__kwargs = kwargs
        self.__args = args
        self.__dict = self._get_result()

        if Data.EVENT is False:
            Data.EVENT = self.heartbeat()
        if track:
            self.track()

    def __repr__(self):
        return json.dumps(
            OrderedDict(
                sorted(self.__dict.items(), key=lambda e: e[0])
            ), indent=2
        )

    def __getattr__(self, attr):
        try:
            return Data.__getattribute__(self, attr)
        except Exception:
            if attr in self.__dict:
                return self.__dict[attr]
            else:
                raise AttributeError("field '%s' can not be found" % attr)

    def _get_result(self):
        result = self.__endpoint(*self.__args, **self.__kwargs)
        if dposlib.rest.cfg.familly == "lisk.v10":
            if isinstance(result, list):
                return result[0]
            elif isinstance(result, dict):
                return result
        else:
            if isinstance(result, dict):
                return result.get("data", result)
            else:
                return result

    def update(self):
        result = self._get_result()
        for key in [k for k in self.__dict if k not in result]:
            self.__dict.pop(key, False)
        self.__dict.update(**result)

    def track(self):
        try:
            Data.REF.add(weakref.ref(self))
        except Exception:
            pass


###########################
# bridges for 2.5 and 2.6 #
###########################
def _username(cls):
    if "attributes" in cls._Data__dict:
        return cls.attributes.get("delegate", {}).get("username", None)
    else:
        return cls._Data__dict.get("username", None)


def _secondPublicKey(cls):
    if "attributes" in cls._Data__dict:
        return cls.attributes.get("secondPublicKey", None)
    else:
        return cls._Data__dict.get("secondPublicKey", None)
############################


class Wallet(Data):
    # bridges for 2.5 and 2.6
    username = property(lambda cls: _username(cls), None, None, "")
    secondPublicKey = property(
        lambda cls: _secondPublicKey(cls), None, None, ""
    )

    def link(self, secret=None, secondSecret=None):
        self.unlink()
        try:
            keys = dposlib.core.crypto.getKeys(
                secret if secret is not None else
                getpass.getpass("secret > ")
            )
            # uncreated wallet
            if not hasattr(self, "publicKey") \
               or getattr(self, "publicKey", None) is None:
                while dposlib.core.crypto.getAddress(
                    keys.get("publicKey", " ")
                ) != self.address:
                    keys = dposlib.core.crypto.getKeys(
                        getpass.getpass("secret > ")
                    )
            else:
                while keys.get("publicKey", None) != self.publicKey:
                    keys = dposlib.core.crypto.getKeys(
                        getpass.getpass("secret > ")
                    )
            if self.secondPublicKey is not None:
                keys_2 = dposlib.core.crypto.getKeys(
                    secondSecret if secondSecret is not None else
                    getpass.getpass("second secret > ")
                )
                while keys_2.get("publicKey", None) != self.secondPublicKey:
                    keys_2 = dposlib.core.crypto.getKeys(
                        getpass.getpass("second secret > ")
                    )
            else:
                keys_2 = {}
        except KeyboardInterrupt:
            sys.stdout.write("\n")
            return False
        else:
            self._publicKey = keys["publicKey"]
            self._privateKey = keys["privateKey"]
            if len(keys_2):
                self._secondPublicKey = keys_2["publicKey"]
                self._secondPrivateKey = keys_2["privateKey"]
            return True

    def setFeeLevel(self, fee_level=None):
        if fee_level is None:
            Transaction.useStaticFee()
        else:
            Transaction.useDynamicFee(fee_level)

    def _finalizeTx(self, tx, fee=None, fee_included=False):
        if hasattr(self, "_publicKey"):
            tx.senderPublicKey = self._publicKey
            tx._privateKey = self._privateKey
        if hasattr(self, "_secondPrivateKey"):
            tx._secondPublicKey = self._secondPublicKey
            tx._secondPrivateKey = self._secondPrivateKey
        tx.finalize(fee=fee, fee_included=fee_included)
        return tx

    @Data.wallet_islinked
    def send(self, amount, address, vendorField=None, fee_included=False):
        "See :func:`dposlib.ark.v2.transfer`."
        tx = dposlib.core.transfer(amount, address, vendorField)
        return dposlib.core.broadcastTransactions(
            self._finalizeTx(tx, fee_included=fee_included)
        )

    @Data.wallet_islinked
    def registerSecondSecret(self, secondSecret):
        "See :func:`dposlib.ark.v2.registerSecondSecret`."
        tx = dposlib.core.registerSecondSecret(secondSecret)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @Data.wallet_islinked
    def registerSecondPublicKey(self, secondPublicKey):
        "See :func:`dposlib.ark.v2.registerSecondPublicKey`."
        tx = dposlib.core.registerSecondPublicKey(secondPublicKey)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @Data.wallet_islinked
    def registerAsDelegate(self, username):
        "See :func:`dposlib.ark.v2.registerAsDelegate`."
        tx = dposlib.core.registerAsDelegate(username)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @Data.wallet_islinked
    def upVote(self, *usernames):
        "See :func:`dposlib.ark.v2.upVote`."
        tx = dposlib.core.upVote(*usernames)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @Data.wallet_islinked
    def downVote(self, *usernames):
        "See :func:`dposlib.ark.v2.downVote`."
        tx = dposlib.core.downVote(*usernames)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))
