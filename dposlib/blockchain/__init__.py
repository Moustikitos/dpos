# -*- coding: utf-8 -*-
# © Toons

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
    First argument of decorated function have to be a `Content` or an
    object containing a valid `address`, `_derivationPath` or `publicKey`
    attribute. It executes the decorated `function` if the object is correctly
    linked using [`dposlib.blockchain.link`](blockchain.md#link) definition.
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
    Associates crypto keys into a [`dposlib.blockchain.Content`](
        blockchain.md#content-objects
    ) object according to secrets. If `secret` or `secondSecret` are not `str`,
    they are considered as `None`.

    Args:
        cls (Content): content object.
        secret (str): secret string. Default set to `None`.
        secondSecret (str): second secret string. Default set to `None`.

    Returns:
        bool: True if secret and second secret match.
    """
    if not hasattr(cls, "address") or not hasattr(cls, "publicKey"):
        raise AttributeError("%s seems not to be linkable" % cls)
    # clean up private attributes
    unlink(cls)
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


def unlink(cls):
    """
    Remove crypto keys association.
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

    ```python
    >>> jsdic = blockchain.JSDict(value=5)
    >>> jsdic
    {'value': 5}
    >>> jsdic.value
    5
    ```
    """
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def __setitem__(self, item, value):
        raise KeyError("%s is readonly" % self.__class__)

    def __delitem__(self, item):
        raise KeyError("%s is readonly" % self.__class__)

    def pop(self, value, default):
        raise KeyError("%s is readonly" % self.__class__)

    def update(self, *args, **kwargs):
        raise KeyError("%s is readonly" % self.__class__)

    __setattr__ = __setitem__
    __getattr__ = dict.__getitem__


class Content(object):
    """
    Live object connected to blockchain. It is initialized with
    `dposlib.rest.GET` request. Object is updated every 30s. Endpoint response
    can be a `dict` or a `list`. If it is a `list`, it is stored in `data`
    attribute else all fields are stored as instance attribute.

    ```python
    >>> txs = blockchain.Content(rest.GET.api.transactions)
    >>> txs.data[0]["timestamp"]
    {
        'epoch': 121912776,
        'unix': 1612013976,
        'human': '2021-01-30T13:39:36.000Z'
    }
    >>> tx = blockchain.Content(
        rest.GET.api.transactions,
        "d36a164a54df9d1c7889521ece15318d6945e9971fecd0a96a9c18e74e0adbf9",
    )
    >>> tx.timestamp
    {
        'epoch': 121919704,
        'unix': 1612020904,
        'human': '2021-01-30T15:35:04.000Z'
    }
    >>> tx.amount
    212963052
    >>> tx.datetime
    datetime.datetime(2021, 1, 30, 15, 35, 4, tzinfo=<UTC>)
    ```

    Args:
        ndpt (usrv.req.Endpoint): endpoint class to be called.
        *args: Variable length argument list used by `usrv.req.Endpoint`.
        **kwargs: Arbitrary keyword arguments used by `usrv.req.Endpoint`.
    """

    REF = set()
    EVENT = False

    datetime = property(
        lambda cls: slots.getRealTime(cls.timestamp["epoch"]),
        None, None, "Associated python datetime object"
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

    def get(self, item, default=None):
        return getattr(self, item, default)

    def filter(self, data):
        if not isinstance(data, dict):
            return JSDict(data=data)
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
    """
    Wallet root class that implements basic wallet behaviour.

    Arguments:
        ndpt (usrv.req.Endpoint): endpoint class to be called.
        fee (int or str): set fee level as `fee multiplier` integer or one of
            `minFee`, `avgFee`, `maxFee` string.
        fee_included (bool): set to True if amout + fee is the total desired
            out flow
        *args: Variable length argument list used by
            `dposlib.blockchain.Content`.
        **kwargs: Arbitrary keyword arguments used by
            `dposlib.blockchain.Content`.
    """

    delegate = property(
        lambda cls: cls.attributes.get("delegate", None),
        None,
        None,
        "Delegate attributes if wallet is registered as delegate"
    )
    username = property(
        lambda cls: cls.attributes.get("delegate", {}).get("username", None),
        None,
        None,
        "Delegate username if wallet is registered as delegate"
    )
    secondPublicKey = property(
        lambda cls: cls.attributes.get("secondPublicKey", None),
        None,
        None,
        "Second public key if second signature is set to wallet"
    )

    def __init__(self, ndpt, *args, **kwargs):
        self._fee_included = kwargs.pop("fee_included", False)
        self._fee = str(kwargs.pop("fee", None))
        Content.__init__(self, ndpt, *args, **kwargs)

    def _finalizeTx(self, tx):
        if hasattr(self, "_publicKey"):
            tx.senderPublicKey = self._publicKey
            tx._privateKey = self._privateKey
        if hasattr(self, "_secondPrivateKey"):
            tx._secondPublicKey = self._secondPublicKey
            tx._secondPrivateKey = self._secondPrivateKey
        tx.finalize(fee=self._fee, fee_included=self._fee_included)
        return tx

    def link(self, *args, **kwargs):
        "See [`dposlib.blockchain.link`](blockchain.md#link)."
        link(self, *args, **kwargs)

    def unlink(self):
        "See [`dposlib.blockchain.unlink`](blockchain.md#unlink)."
        unlink(self)

    @isLinked
    def send(self, amount, address, vendorField=None):
        "See [`dposlib.ark.v2.transfer`](v2.md#transfer)."
        tx = dposlib.core.transfer(amount, address, vendorField)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @isLinked
    def registerSecondSecret(self, secondSecret):
        """
        See [`dposlib.ark.v2.registerSecondSecret`](
            v2.md#registersecondsecret
        ).
        """
        tx = dposlib.core.registerSecondSecret(secondSecret)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @isLinked
    def registerSecondPublicKey(self, secondPublicKey):
        """
        See [`dposlib.ark.v2.registerSecondPublicKey`](
            v2.md#registersecondpublickey
        ).
        """
        tx = dposlib.core.registerSecondPublicKey(secondPublicKey)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @isLinked
    def registerAsDelegate(self, username):
        """
        See [`dposlib.ark.v2.registerAsDelegate`](
            v2.md#registerasdelegate
        ).
        """
        tx = dposlib.core.registerAsDelegate(username)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @isLinked
    def upVote(self, *usernames):
        "See [`dposlib.ark.v2.upVote`](v2.md#upvote)."
        tx = dposlib.core.upVote(*usernames)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @isLinked
    def downVote(self, *usernames):
        "See [`dposlib.ark.v2.downVote`](v2.md#downvote)."
        tx = dposlib.core.downVote(*usernames)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))
