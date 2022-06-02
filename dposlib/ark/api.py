# -*- coding: utf-8 -*-

import os
import re
import sys
import json
import pickle
import weakref
import hashlib
import getpass
import inspect
import dposlib

from dposlib.ark import slots, crypto
from dposlib.util.data import filter_dic, dumpJson, loadJson
from dposlib.util.asynch import setInterval
from dposlib.ark.mixin import loadPages, deltas

try:
    from dposlib.ark import ldgr
    LEDGERBLUE = True
except ImportError:
    LEDGERBLUE = False

deltas = deltas
GET = dposlib.rest.GET


def isLinked(func):
    """
    `Python decorator`.
    First argument of decorated function have to be a
    [`dposlib.ark.api.Content`](api.md#dposlib.ark.api.Content)
    or an object containing a valid `address`, `_derivationPath` or `publicKey`
    attribute. It executes the decorated `function` if the object is correctly
    linked using `dposlib.ark.api.link` definition.
    """
    def wrapper(*args, **kw):
        obj = args[0]
        # if already linked... or if ledger Wallet class
        if getattr(obj, "_isLinked", False) or hasattr(obj, "_derivationPath"):
            return func(*args, **kw)

        if not hasattr(obj, "address") \
           or getattr(obj, "attributes", {}).get("multiSignature", False):
            raise Exception("can not be linked with secrets")
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
    Associates crypto keys into a [`dposlib.ark.api.Content`](
        api.md#dposlib.ark.api.Content
    ) object according to secrets. If `secret` or `secondSecret` are not `str`,
    they are considered as `None`. In this case secrets will be asked and
    checked from console untill success or `Ctrl+c` keyboard interruption.

    Args:
        cls (Content): content object.
        secret (str): secret string. Default set to `None`.
        secondSecret (str): second secret string. Default set to `None`.

    Returns:
        bool: True if secret and second secret match.
    """
    if not hasattr(cls, "address") \
       or not hasattr(cls, "publicKey") \
       or getattr(cls, "attributes", {}).get("multiSignature", False):
        raise AttributeError("%s seems not to be linkable" % cls)
    # clean up private attributes
    unlink(cls)
    # filter args according to their types. Considered as None if neither str
    # or unicode
    loop_secret = not isinstance(secret, str)
    loop_secondSecret = not isinstance(secondSecret, str)
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
        cls._isLinked = True
        return True


def unlink(cls):
    """
    Remove crypto keys association.
    """
    for attr in [
        '_isLinked',
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
    >>> jsdic = dposlib.ark.JSDict(value=5)
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
    [`dposlib.rest.GET`](../rest.md#dposlib.rest.GET) request. Object is
    updated every 30s. Endpoint response can be a `dict` or a `list`. If it is
    a `list`, it is stored in `data` attribute else all fields are stored as
    instance attribute.

    ```python
    >>> txs = dposlib.ark.Content(rest.GET.api.transactions)
    >>> txs.data[0]["timestamp"]
    {
        'epoch': 121912776,
        'unix': 1612013976,
        'human': '2021-01-30T13:39:36.000Z'
    }
    >>> tx = dposlib.ark.Content(
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
    """

    REF = set()
    EVENT = False

    datetime = property(
        lambda cls: slots.getRealTime(cls.timestamp["epoch"]),
        None, None, "Associated python datetime object"
    )

    def __init__(self, ndpt, *args, **kwargs):
        """
        Args:
            ndpt (usrv.req.Endpoint): endpoint class to be called.
            *args: Variable length argument list used by `usrv.req.Endpoint`.

        **Kwargs**:

        * `keep_alive` *bool* - set hook to update data from blockcahin.
            Default to True.
        """
        track = kwargs.pop("keep_alive", True)
        self.__ndpt = ndpt
        self.__args = args
        self.__kwargs = kwargs
        self.update()

        if track:
            self.track()

        if Content.EVENT is False:
            Content.EVENT = setInterval(30)(contentUpdate)()

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
        """
        Convert data as JSDict object converting string values in int if
        possible.
        """
        if not isinstance(data, dict):
            return JSDict(data=data)
        for k in data:
            v = data[k]
            if isinstance(v, dict):
                data[k] = self.filter(v)
            elif isinstance(v, str):
                if re.match(r"^[0-9]*$", v):
                    data[k] = int(v)
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
    """
    #: Delegate attributes if wallet is registered as delegate.
    delegate = property(
        lambda cls: cls.attributes.get("delegate", None),
        None,
        None,
        "Delegate attributes if wallet is registered as delegate"
    )
    #: Delegate username if wallet is registered as delegate.
    username = property(
        lambda cls: cls.attributes.get("delegate", {}).get("username", None),
        None,
        None,
        "Delegate username if wallet is registered as delegate"
    )
    #: Second public key if second signature is set to wallet.
    secondPublicKey = property(
        lambda cls: cls.attributes.get("secondPublicKey", None),
        None,
        None,
        "Second public key if second signature is set to wallet"
    )

    def __init__(self, address, **kw):
        """
        Args:
            address (str): wallet address or delegate username.
            **kwargs: Variable key argument used by
                [`dposlib.ark.api.Content`](api.md#dposlib.ark.api.Content).

        **Specific kwargs**:

        * `keep_alive` *bool* - automatic update data from blockcahin. Default
            to True.
        * `fee` *int or str* - set fee level as fee multiplier string value or
            one of **minFee**, **avgFee**, **maxFee**. Default to **avgFee**.
        * `fee_included` *bool* - set to True if amout + fee is the total
            desired out flow. Default to False.
        """
        self._fee_included = kw.pop("fee_included", False)
        self._fee = str(kw.pop("fee", "avgFee"))
        Content.__init__(
            self, GET.api.wallets, address, **dict({"returnKey": "data"}, **kw)
        )

    def _finalizeTx(self, tx):
        if hasattr(self, "_privateKey"):
            # set publicKey manualy
            dict.__setitem__(tx, "senderPublicKey", self.publicKey)
            tx["nonce"] = self.nonce + 1
            tx["senderId"] = self.address
            if tx["type"] not in [0, 8]:
                tx["recipientId"] = self.address
            tx.fee = self._fee
            tx.feeIncluded = self._fee_included
            tx["signature"] = crypto.getSignatureFromBytes(
                crypto.getBytes(tx), self._privateKey
            )
            if hasattr(self, "_secondPrivateKey"):
                tx["signSignature"] = \
                    crypto.getSignatureFromBytes(
                        crypto.getBytes(tx),
                        self._secondPrivateKey
                    )
            tx["id"] = crypto.getIdFromBytes(
                crypto.getBytes(tx, exclude_multi_sig=False)
            )
        return tx

    def _broadcastTx(self, tx):
        resp = dposlib.rest.POST.api.transactions(
            transactions=[self._finalizeTx(tx)]
        )
        if len(resp.get("data", {}).get("accept", [])) == 1:
            self.__dict__["nonce"] += 1
        return resp

    def link(self, *args, **kwargs):
        "See [`dposlib.ark.api.link`](api.md#dposlib.ark.api.link)."
        link(self, *args, **kwargs)

    def unlink(self):
        "See [`dposlib.ark.api.unlink`](api.md#dposlib.ark.api.unlink)."
        unlink(self)

    @isLinked
    def send(self, amount, address, vendorField=None, expiration=0):
        """
        Broadcast a transfer transaction to the ledger.
        See [`dposlib.ark.builders.v2.transfer`](
            builders/v2.md#dposlib.ark.builders.v2.transfer
        ).
        """
        return self._broadcastTx(
            dposlib.core.transfer(amount, address, vendorField, expiration)
        )

    @isLinked
    def setSecondSecret(self, secondSecret):
        """
        Broadcast a second secret registration transaction to the ledger.
        See [`dposlib.ark.builders.v2.registerSecondSecret`](
            builders/v2.md#dposlib.ark.builders.v2.registerSecondSecret
        ).
        """
        return self._broadcastTx(
            dposlib.core.registerSecondSecret(secondSecret)
        )

    @isLinked
    def setSecondPublicKey(self, secondPublicKey):
        """
        Broadcast a second secret registration transaction into the ledger.
        See [`dposlib.ark.builders.v2.registerSecondPublicKey`](
            builders/v2.md#dposlib.ark.builders.v2.registerSecondPublicKey
        ).
        """
        return self._broadcastTx(
            dposlib.core.registerSecondPublicKey(secondPublicKey)
        )

    @isLinked
    def setDelegate(self, username):
        """
        Broadcast a delegate registration transaction to the ledger.
        See [`dposlib.ark.builders.v2.registerAsDelegate`](
            builders/v2.md#dposlib.ark.builders.v2.registerAsDelegate
        ).
        """
        return self._broadcastTx(dposlib.core.registerAsDelegate(username))

    @isLinked
    def upVote(self, *usernames):
        """
        Broadcast an up-vote transaction to the ledger.
        See [`dposlib.ark.builders.v2.switchVote`](
            builders/v2.md#dposlib.ark.builders.v2.switchVote
        )."""
        tx = dposlib.core.upVote(*usernames)
        if self.attributes.vote is not None:
            tx["asset"]["votes"].insert(0, "-" + self.attributes.vote)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @isLinked
    def downVote(self, *usernames):
        """
        Broadcast a down-vote transaction to the ledger.
        See [`dposlib.ark.builders.v2.downVote`](
            builders/v2.md#dposlib.ark.builders.v2.downVote
        ).
        """
        return self._broadcastTx(dposlib.core.downVote(*usernames))

    @isLinked
    def sendIpfs(self, ipfs):
        """
        See [`dposlib.ark.builders.v2.registerIpfs`](
            builders/v2.md#dposlib.ark.builders.v2.registerIpfs
        )."""
        tx = dposlib.core.registerIpfs(ipfs)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @isLinked
    def multiSend(self, *pairs, **kwargs):
        """
        See [`dposlib.ark.builder.multiPayment`](
            builders/v2.md#dposlib.ark.builders.v2.multiPayment
        )."""
        tx = dposlib.core.multiPayment(*pairs, **kwargs)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @isLinked
    def resignate(self):
        """
        See [`dposlib.ark.builders.v2.delegateResignation`](
            builders/v2.md#dposlib.ark.builders.v2.delegateResignation
        ).
        """
        tx = dposlib.core.delegateResignation()
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @isLinked
    def sendHtlc(self, amount, address, secret,
                 expiration=24, vendorField=None, hash_type=0):
        """
        See [`dposlib.ark.builders.v2.htlcLock`](
            builders/v2.md#dposlib.ark.builders.v2.htlcLock
        ).
        """
        v3 = "hash_type" in inspect.getfullargspec(dposlib.core.htlcLock).args
        if v3:
            tx = dposlib.core.htlcLock(
                amount, address, secret,
                expiration=expiration, vendorField=vendorField,
                hash_type=hash_type
            )
        else:
            tx = dposlib.core.htlcLock(
                amount, address, secret,
                expiration=expiration, vendorField=vendorField
            )
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @isLinked
    def claimHtlc(self, txid, secret, hash_type=0):
        """
        See [`dposlib.ark.builders.v2.htlcClaim`](
            builders/v2.md#dposlib.ark.builders.v2.htlcClaim
        ).
        """
        v3 = "hash_type" in inspect.getfullargspec(dposlib.core.htlcClaim).args
        if v3:
            tx = dposlib.core.htlcClaim(txid, secret, hash_type)
        else:
            tx = dposlib.core.htlcClaim(txid, secret)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @isLinked
    def refundHtlc(self, txid):
        """
        See [`dposlib.ark.builders.v2.htlcRefund`](
            builders/v2.md#dposlib.ark.builders.v2.htlcRefund
        ).
        """
        tx = dposlib.core.htlcRefund(txid)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @isLinked
    def createEntity(self, name, type="business", subtype=0, ipfsData=None):
        """
        See [`dposlib.ark.builders.v2.entityRegister`](
            builders/v2.md#dposlib.ark.builders.v2.entityRegister
        ).
        """
        tx = dposlib.core.entityRegister(name, type, subtype, ipfsData)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @isLinked
    def updateEntity(self, registrationId, ipfsData, name=None):
        """
        See [`dposlib.ark.builders.v2.entityUpdate`](
            builders/v2.md#dposlib.ark.builders.v2.entityUpdate
        ).
        """
        tx = dposlib.core.entityUpdate(registrationId, ipfsData, name)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @isLinked
    def resignEntity(self, registrationId):
        """
        See [`dposlib.ark.builders.v2.entityResign`](
            builders/v2.md#dposlib.ark.builders.v2.entityResign
        ).
        """
        tx = dposlib.core.entityResign(registrationId)
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))


class Ledger(Wallet):
    """
    Ledger wallet api.
    """

    d_path = re.compile(r"^44'/[0-9]*'/[0-9]*'/[0-9]/[0-9]$")

    def __init__(self, account=0, index=0, network=0, **kw):
        if not LEDGERBLUE:
            raise Exception("ledgerblue is not installed")
        self._debug = kw.pop("debug", False)
        self._schnorr = kw.pop("schnorr", True)

        # aip20 : https://github.com/ArkEcosystem/AIPs/issues/29
        d_path = kw.pop("derivation_path", kw.pop("path", False))
        if d_path is not False:
            if Ledger.d_path.match(d_path) is not None:
                self._derivationPath
            else:
                raise Exception("%s not a valid derivation path" % d_path)
        else:
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
            self, "address", crypto.getAddress(puk)
        )
        Wallet.__init__(self, self.address, **kw)

    def _finalizeTx(self, tx):
        if "fee" not in tx or self._fee is not None:
            tx.fee = self._fee
        tx.feeIncluded = self._fee_included
        tx["senderPublicKey"] = self.publicKey
        tx["signature"] = ldgr.sendApdu(
            ldgr.buildSignatureApdu(
                crypto.getBytes(tx),
                self._dongle_path,
                "tx",
                self._schnorr
            ),
            debug=self._debug
        )

        if tx._secondPublicKey is not None:
            try:
                k2 = crypto.getKeys(
                    getpass.getpass("second secret > ")
                )
                while k2.get("publicKey", None) != tx._secondPublicKey:
                    k2 = crypto.getKeys(
                        getpass.getpass("second secret > ")
                    )
            except KeyboardInterrupt:
                raise Exception("transaction cancelled")
            else:
                tx["signSignature"] = crypto.getSignature(
                    tx, k2["privateKey"]
                )

        tx.identify()
        return tx


class Delegate(Content):

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
        Content.__init__(
            self, GET.api.delegates, username,
            **dict({"returnKey": "data"}, **kw)
        )

    def getRecentBlocks(self, limit=50):
        return loadPages(
            GET.api.delegates.__getattr__(self.username).blocks,
            limit=limit
        )


class Block(Content):

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
        Content.__init__(
            self, GET.api.blocks, blk_id, **dict({"returnKey": "data"}, **kw)
        )


class Webhook(Content):
    """
    ```python
    >>> import dposlib
    >>> peer = "http:/127.0.0.1:4004"
    >>> target = "http://127.0.0.1/targetted/endpoint"
    >>> wh = dposlib.core.api.Webhook(
    ...   peer, "transaction.applied", target, "amount<1"
    ... )
    security token: 9f86d081884c7d659a2feaa0c55ad015...2b0b822cd15d6c15b0f00a08
    >>> dposlib.core.api.webhook.verify("9f86d081884c7d659a2feaa0c55ad015")
    True
    >>> wh.delete()
    {"sucess": True, "status": 204}
    ```
    """

    regexp = re.compile(r'^([\w\.]*)\s*([^\w\s\^]*)\s*(.*)\s*$')
    operators = {
        "<": "lt", "<=": "lte",
        ">": "gt", ">=": "gte",
        "==": "eq", "!=": "ne",
        "?": "truthy", "!?": "falsy",
        "\\": "regexp", "$": "contains",
        "<>": "between", "!<>": "not-between"
    }

    @staticmethod
    def condition(expr):
        """
        Webhook condition builder from `str` expression. It is internally used
        by [`Webhook.create`](api.md#dposlib.ark.api.Webhook.create) method.

        <style>td,th{border:none!important;text-align:left;}</style>
        webhook                   | dposlib
        ------------------------- | ------------
        `lt` / `lte`              | `<` / `<=`
        `gt` / `gte`              | `>` / `>=`
        `eq` / `ne`               | `==` / `!=`
        `truthy` / `falsy`        | `?` / `!?`
        `regexp` / `contains`     | `\\` / `$`
        `between` / `not-between` | `<>` / `!<>`

        ```python
        >>> import dposlib.ark.api as api
        >>> api.Webhook.condition("vendorField\\^.*payroll.*$")
        {'value': '^.*payroll.*$', 'key': 'vendorField', 'condition': 'regexp'}
        >>> api.Webhook.condition("amount<>2000000000000:4000000000000")
        {
            'value': {'min': '2000000000000', 'max': '4000000000000'},
            'condition': 'between',
            'key': 'amount'
        }
        ```

        Args:
            expr (str): human readable expression.

        Returns:
            dict: webhook conditions
        """
        condition = {}
        try:
            key, _operator, value = Webhook.regexp.match(expr).groups()
            operator = Webhook.operators[_operator]
        except Exception as error:
            print(">>> %r" % error)
        else:
            if "between" in operator:
                _min, _max = value.split(":")
                condition["value"] = {"min": _min, "max": _max}
            elif value != "":
                condition["value"] = value
            condition["key"] = key
            condition["condition"] = operator
        return condition

    @staticmethod
    def dump(token):
        # token =
        # "0c8e74e1cbfe36404386d33a5bbd8b66fe944e318edb02b979d6bf0c87978b64"
        authorization = token[:32]  # "fe944e318edb02b979d6bf0c87978b64"
        verification = token[32:]   # "0c8e74e1cbfe36404386d33a5bbd8b66"
        filename = os.path.join(
            dposlib.ROOT, ".webhooks", dposlib.rest.cfg.network,
            hashlib.md5(authorization.encode("utf-8")).hexdigest()
        )
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb") as out:
            pickle.dump(
                {
                    "verification": verification,
                    "hash": hashlib.sha256(token.encode("utf-8")).hexdigest()
                },
                out
            )
        return filename

    @staticmethod
    def create(peer, event, target, *conditions):
        conditions = [
            (
                Webhook.condition(cond) if isinstance(cond, str) else
                cond if isinstance(cond, dict) else
                {}
            )
            for cond in conditions
        ]
        data = dposlib.rest.POST.api.webhooks(
            peer=peer, event=event, target=target,
            conditions=[cond for cond in conditions if cond],
            returnKey="data"
        )
        if "token" in data:
            print("security token :", data["token"])
            # build the security hash and keep only second token part and
            # save the used peer to be able to delete it later
            data["dump"] = Webhook.dump(data.pop("token"))
            data["peer"] = peer
            dumpJson(
                data, os.path.join(
                    dposlib.ROOT, ".webhooks", dposlib.rest.cfg.network,
                    data["id"] + ".json"
                )
            )
            return Webhook(data["id"], peer=peer)
        else:
            raise Exception("webhook not created")

    @staticmethod
    def verify(authorization):
        filename = os.path.join(
            dposlib.ROOT, ".webhooks", dposlib.rest.cfg.network,
            hashlib.md5(authorization.encode("utf-8")).hexdigest()
        )
        try:
            with open(filename, "rb") as in_:
                data = pickle.load(in_)
        except Exception:
            return False
        else:
            token = authorization + data["verification"]
            return hashlib.sha256(
                token.encode("utf-8")
            ).hexdigest() == data["hash"]

    @staticmethod
    def list():
        return [
            name for name in next(
                os.walk(
                    os.path.join(
                        dposlib.ROOT, ".webhooks", dposlib.rest.cfg.network
                    )
                )
            )[-1] if name.endswith(".json")
        ]

    @staticmethod
    def open(whk_id):
        data = loadJson(
            os.path.join(
                dposlib.ROOT, ".webhooks", dposlib.rest.cfg.network, whk_id
            )
        )
        if len(data):
            return Webhook(data["id"], peer=data["peer"])
        else:
            raise Exception("cannot open webhook %s" % whk_id)

    def __init__(self, whk_id, **kw):
        Content.__init__(
            self, GET.api.webhooks, "%s" % whk_id,
            **dict({"keep_alive": False, "returnKey": "data"}, **kw)
        )

    def delete(self):
        whk_path = os.path.join(
            dposlib.ROOT, ".webhooks", dposlib.rest.cfg.network,
            self.id + ".json"
        )
        if os.path.exists(whk_path):
            data = loadJson(whk_path)
            resp = dposlib.rest.DELETE.api.webhooks(
                "%s" % self.id, peer=data.get("peer", None)
            )
            if resp.get("status", None) == 204:
                try:
                    os.remove(data["dump"])
                except Exception:
                    pass
                os.remove(whk_path)
            resp.pop('except', False)
            resp.pop('error', False)
            return resp
        else:
            raise Exception("cannot find webhook data")

    # TODO: implement
    def change(self, event=None, target=None, *conditions):
        pass
