# -*- coding: utf-8 -*-
# © Toons

"""
:mod:`dposlib.blockchain` package provides :class:`Content` and
:class:`Wallet` classes.

>>> from dposlib import rest
>>> rest.use("dark")
True
>>> # initialize wallet using rest endpoint
>>> wlt = blockchain.Wallet(rest.GET.api.wallets.darktoons)
>>> wlt.address
'D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk'
"""

import re
import sys
import json
import weakref
import getpass

import dposlib
import dposlib.rest
from dposlib.blockchain import slots
from dposlib.util.asynch import setInterval

if dposlib.PY3:
    long = int
    unicode = str


def isLinked(func):
    """
    `Python decorator`.
    First argument of decorated function have to be a
    :class:`Content` or an object containing a valid :attr:`address`,
    :attr:`derivationPath` or :attr:`publicKey` attribute. It executes the
    decorated :func:`function` if the object is correctly linked using
    :func:`dposlib.blockchain.link`.
    """
    def wrapper(*args, **kw):
        obj = args[0]
        if hasattr(obj, "_derivationPath"):
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


def link(cls, secret=None, secondSecret=None):
    """
    Associates crypto keys into an :class:`Content` object according to
    secrets. If :attr:`secret` or :attr:`secondSecret` are not :class:`str`,
    they are considered as :attr:`None`.

    Arguments:
        cls (:class:`Content`): content object
        secret (:class:`str`): secret string
        secondSecret (:class:`str`): second secret string
    Returns:
        :class:`bool`: True if secret and second secret match crypto keys
    """
    if not hasattr(cls, "address") or not hasattr(cls, "publicKey"):
        raise AttributeError("%s seems not to be linkable" % cls)
    # clean up private attributes
    unLink(cls)
    # filter args according to their types. Considered as None if neither str
    # or unicode
    loop_secret = not isinstance(secret, (str, unicode))
    loop_secondSecret = not isinstance(secondSecret, (str, unicode))
    # try loop to catch keyboard interuption to exit while loops
    try:
        keys = dposlib.core.crypto.getKeys(
            getpass.getpass("secret > ") if loop_secret else secret
        )
        # uncreated wallet has no publicKey so check over address
        if getattr(cls, "publicKey", None) is None:
            # return False if given secret does not match address
            if (
                not loop_secret
                and dposlib.core.crypto.getAddress(
                    keys.get("publicKey", "?")
                ) != cls.address
            ):
                return False
            # exit while loop only if keyboard-given secret matches the address
            while loop_secret and dposlib.core.crypto.getAddress(
                keys.get("publicKey", "?")
            ) != cls.address:
                keys = dposlib.core.crypto.getKeys(
                    getpass.getpass("secret > ")
                )
        elif loop_secret:
            # return False if given secret does not match publicKey
            if (
                not loop_secret
                and keys.get("publicKey", None) != cls.publicKey
            ):
                return False
            # exit while loop only if keyboard-given secret matches the
            # public key
            while keys.get("publicKey", None) != cls.publicKey:
                keys = dposlib.core.crypto.getKeys(
                    getpass.getpass("secret > ")
                )
        # if a second public key is defined
        if getattr(cls, "secondPublicKey", None) is not None:
            keys_2 = dposlib.core.crypto.getKeys(
                getpass.getpass("second secret > ")
                if loop_secondSecret else secondSecret
            )
            if (
                not loop_secondSecret
                and keys_2.get("publicKey", None) != cls.secondPublicKey
            ):
                return False
            # exit while loop only if keyboard-given secret matches the
            # second public key
            while loop_secondSecret and keys_2.get(
                "publicKey", "?"
            ) != cls.secondPublicKey:
                keys_2 = dposlib.core.crypto.getKeys(
                    getpass.getpass("second secret > ")
                )
        else:
            keys_2 = {}
    except KeyboardInterrupt:
        sys.stdout.write("\n")
        return False
    else:
        cls._publicKey = keys["publicKey"]
        cls._privateKey = keys["privateKey"]
        if len(keys_2):
            cls._secondPublicKey = keys_2["publicKey"]
            cls._secondPrivateKey = keys_2["privateKey"]
        return True


def unLink(cls):
    """
    Remove crypot keys association.
    """
    for attr in [
        '_privateKey',
        '_publicKey',
        '_secondPublicKey',
        '_secondPrivateKey'
    ]:
        if hasattr(cls, attr):
            delattr(cls, attr)


class JSDict(dict):
    """
    Read only dictionary with js object behaviour.
    """
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def __setitem__(self, item, value):
        raise KeyError("%s is readonly" % self.__class__)

    def __delitem__(self, item):
        raise KeyError("%s is readonly" % self.__class__)

    def pop(self, value, default):
        ""
        raise KeyError("%s is readonly" % self.__class__)

    def update(self, *args, **kwargs):
        ""
        raise KeyError("%s is readonly" % self.__class__)

    __setattr__ = __setitem__
    __getattr__ = dict.__getitem__


class Content(object):
    """
    """

    REF = set()
    EVENT = False

    datetime = property(
        lambda cls: slots.getRealTime(cls.timestamp["epoch"]),
        None, None, ""
    )

    def __init__(self, ndpt, *args, **kwargs):
        track = kwargs.pop("keep_alive", True)
        self.__ndpt = ndpt
        self.__args = args
        self.__kwargs = kwargs
        self.update()

        if track:
            self.track()

        if Content.EVENT is False:
            Content.EVENT = contentUpdate()

    def __str__(self):
        return json.dumps(
            dict([k, v] for k, v in self.__dict__.items() if k[0] != "_"),
            sort_keys=True
        )

    def __repr__(self):
        return json.dumps(
            dict([k, v] for k, v in self.__dict__.items() if k[0] != "_"),
            indent=2, sort_keys=True
        )

    def __setattr__(self, attr, value):
        if attr[0] != "_":
            raise AttributeError("%s is read only attribute" % attr)
        else:
            object.__setattr__(self, attr, value)
    __setitem__ = __setattr__

    def __delattr__(self, attr):
        if attr[0] != "_":
            raise AttributeError("%s is readonly attribute" % attr)
        else:
            object.__delattr__(self, attr)

    def __getitem__(self, item):
        return getattr(self, item)

    def get(self, item, default):
        return getattr(self, item, default)

    def filter(self, data):
        for k in data:
            v = data[k]
            if isinstance(v, dict):
                data[k] = self.filter(v)
            elif isinstance(v, (str, unicode)):
                if re.match(r"^[0-9]*$", v):
                    data[k] = long(v)
        return JSDict(data)

    def update(self):
        result = self.__ndpt(*self.__args, **self.__kwargs)
        if isinstance(result, dict):
            if result.get("status", 0) < 300:
                self.__dict__.update(
                    self.filter(result.get("data", result))
                )

    def track(self):
        try:
            Content.REF.add(weakref.ref(self))
        except Exception:
            pass


@setInterval(30)
def contentUpdate():
    dead = set()
    for ref in list(Content.REF):
        obj = ref()
        if obj:
            obj.update()
        else:
            dead.add(ref)
    Content.REF -= dead
    if len(Content.REF) == 0:
        Content.EVENT.set()
        Content.EVENT = False


class Wallet(Content):

    delegate = property(
        lambda cls: cls.attributes.get("delegate", None),
        None,
        None,
        ""
    )
    username = property(
        lambda cls: cls.attributes.get("delegate", {}).get("username", None),
        None,
        None,
        ""
    )
    secondPublicKey = property(
        lambda cls: cls.attributes.get("secondPublicKey", None),
        None,
        None,
        ""
    )

    def _finalizeTx(self, tx, fee=None, fee_included=False):
        if hasattr(self, "_publicKey"):
            tx.senderPublicKey = self._publicKey
            tx._privateKey = self._privateKey
        if hasattr(self, "_secondPrivateKey"):
            tx._secondPublicKey = self._secondPublicKey
            tx._secondPrivateKey = self._secondPrivateKey
        tx.finalize(fee=fee, fee_included=fee_included)
        return tx

    @isLinked
    def send(self, amount, address, vendorField=None, fee_included=False):
        "See :func:`dposlib.ark.v2.transfer`."
        tx = dposlib.core.transfer(amount, address, vendorField)
        return dposlib.core.broadcastTransactions(
            self._finalizeTx(tx, fee_included=fee_included)
        )

    @isLinked
    def registerSecondSecret(self, secondSecret):
        "See :func:`dposlib.ark.v2.registerSecondSecret`."
        tx = dposlib.core.registerSecondSecret(secondSecret)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @isLinked
    def registerSecondPublicKey(self, secondPublicKey):
        "See :func:`dposlib.ark.v2.registerSecondPublicKey`."
        tx = dposlib.core.registerSecondPublicKey(secondPublicKey)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @isLinked
    def registerAsDelegate(self, username):
        "See :func:`dposlib.ark.v2.registerAsDelegate`."
        tx = dposlib.core.registerAsDelegate(username)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @isLinked
    def upVote(self, *usernames):
        "See :func:`dposlib.ark.v2.upVote`."
        tx = dposlib.core.upVote(*usernames)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @isLinked
    def downVote(self, *usernames):
        "See :func:`dposlib.ark.v2.downVote`."
        tx = dposlib.core.downVote(*usernames)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))
