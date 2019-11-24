# -*- coding: utf-8 -*-
# © Toons

"""
:mod:`dposlib.blockchain` package provides :class:`Transaction` and
:class:`.Wallet` classes.

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

import os
import sys
import json
import weakref
import getpass

from collections import OrderedDict

import dposlib
import dposlib.rest
from dposlib.blockchain import slots, cfg
from dposlib.util.asynch import setInterval
from dposlib.util.data import loadJson, dumpJson


def track_data(value=True):
    Data.TRACK = value


class Transaction(dict):
    """
    A python :class:`dict` that implements all the necessities to manually
    generate valid transactions.
    """

    DFEES = False
    FMULT = 10000
    FEESL = None

    def _compute_fee(self, value=None):
        try:
            return int(value)
        except Exception:
            static_value = getattr(cfg, "fees", {})\
                .get("staticFees", getattr(cfg, "fees", {}))\
                .get(dposlib.core.TRANSACTIONS[self["type"]], 10000000)
            if Transaction.DFEES:
                feesl = value if isinstance(value, str) else\
                        Transaction.FEESL
                # use fee statistics if FEESL is not None
                # if Transaction.FEESL is not None:
                if feesl is not None and self["type"] not in [6,]:
                    # if fee statistics not found, return static fee value
                    fee = cfg.feestats.get(self["type"], {})\
                          .get(feesl, static_value)
                # else compute fees using fee multiplier and tx size
                else:
                    fee = dposlib.core.computeDynamicFees(self)
            else:
                # k is 0 or signature number in case of multisignature
                # registration
                k = len(
                    self.get("asset", {})
                    .get("multiSignature", {})
                    .get("publicKeys", [])
                )
                fee = static_value * (1+k)
            return int(fee)

    def _setNonce(self, publicKey):
        self["nonce"] = int(
            dposlib.rest.GET.api.wallets(publicKey)
            .get("data", {})
            .get("nonce", 0)
        ) + 1

    def _setSenderPublicKey(self, publicKey):
        dict.__setitem__(self, "senderPublicKey", publicKey)
        if self.get("version", 0x00) >= 0x02:
            if "nonce" not in self:
                self._setNonce(publicKey)
        if "timestamp" not in self:
            self["timestamp"] = slots.getTime()

    @staticmethod
    def path():
        """Return current registry path."""
        if hasattr(Transaction, "_publicKey"):
            return os.path.join(
                dposlib.ROOT, ".registry", cfg.network, Transaction._publicKey
            )
        else:
            raise Exception("No public key found")

    @staticmethod
    def unlink():
        """
        Remove public and private keys. This is equivalent to a wellet logout.
        Once keys removed, no signature is possible.
        """
        for attr in [
            '_privateKey',
            '_publicKey',
            '_secondPublicKey',
            '_secondPrivateKey'
        ]:
            if hasattr(Transaction, attr):
                delattr(Transaction, attr)

    @staticmethod
    def link(secret=None, secondSecret=None):
        """
        Save public and private keys derived from secrets. This is equivalent
        to wallet login. it limits number of secret keyboard entries.

        Args:
            secret (:class:`str`): passphrase
            secondSecret (:class:`str`): second passphrase
        """
        if hasattr(dposlib, "core"):
            if secret:
                keys = dposlib.core.crypto.getKeys(secret)
                Transaction._publicKey = keys["publicKey"]
                Transaction._privateKey = keys["privateKey"]
            if secondSecret:
                keys = dposlib.core.crypto.getKeys(secondSecret)
                Transaction._secondPublicKey = keys["publicKey"]
                Transaction._secondPrivateKey = keys["privateKey"]

    @staticmethod
    def useDynamicFee(value="avgFee"):
        """
        Activate and configure dynamic fees parameters. Value can be either an
        integer defining the fee multiplier constant or a string defining the
        fee level to use acccording to the 30-days-average. possible values are
        ``avgFee`` (default) ``minFee`` and ``maxFee``.

        Args:
            value (:class:`str` or :class:`int`): constant or fee multiplier
        """
        if hasattr(cfg, "doffsets"):
            Transaction.DFEES = True
            if isinstance(value, int):
                Transaction.FMULT = value
                Transaction.FEESL = None
            elif value in ["maxFee", "avgFee", "minFee"]:
                Transaction.FEESL = value
        else:
            raise Exception("Dynamic fees can not be set on %s network" %
                            cfg.network)
    setDynamicFee = useDynamicFee

    @staticmethod
    def useStaticFee():
        """Deactivate dynamic fees."""
        Transaction.DFEES = False
    setStaticFee = useStaticFee

    @staticmethod
    def load(txid):
        """Loads the transaction identified by txid from registry."""
        data = loadJson(Transaction.path())[txid]
        data["senderId"] = dposlib.core.crypto.getAddress(
            data["senderPublicKey"], marker=data.pop("network", False)
        )
        return Transaction(data)

    def __repr__(self):
        return json.dumps(
            OrderedDict(sorted(self.items(), key=lambda e: e[0])), indent=2
        )

    def __init__(self, *args, **kwargs):
        if not hasattr(dposlib, "core"):
            raise Exception("no blockchain loaded")
        data = dict(*args, **kwargs)
        dict.__init__(self)

        version = data.pop("version", 0x0)
        if version >= 0x1:
            self["version"] = version
        if version >= 0x2:
            # default typeGroup is 1 (Ark core)
            self["typeGroup"] = data.pop("typeGroup", 1)
            self["network"] = cfg.pubkeyHash

        self["amount"] = data.pop("amount", 0)  # amount is required field
        self["type"] = data.pop("type", 0)  # default type is 0 (transfer)
        self["asset"] = data.pop("asset", {})  # if no one given

        for key, value in [(k, v) for k, v in data.items() if v is not None]:
            self[key] = value

        if hasattr(Transaction, "_publicKey"):
            self._setSenderPublicKey(Transaction._publicKey)

    def __setitem__(self, item, value):
        # cast values according to transaction typing
        if item in dposlib.core.TYPING.keys():
            cast = dposlib.core.TYPING[item]
            if item == "fee":
                value = self._compute_fee(value)  # self.setFee(value)
            elif item == "vendorField":
                value = value.decode("utf-8") if isinstance(value, bytes)\
                        else value
            elif not isinstance(value, cast):
                value = cast(value)
            dict.__setitem__(self, item, value)
            # remove signatures and ids if an item other than signature or id
            # is modified
            if item not in ["signatures", "signature", "signSignature",
                            "secondSignature", "id"]:
                self.pop("signature", False)
                self.pop("signSignature", False)
                self.pop("secondSignature", False)
                self.pop("id", False)
        # set internal private keys (secrets are not stored)
        elif item == "secret":
            self.link(value)
            self._setSenderPublicKey(Transaction._publicKey)
        elif item == "secondSecret":
            self.link(None, value)
        elif item == "privateKey":
            Transaction._privateKey = str(value)
        elif item == "secondPrivateKey":
            Transaction._secondPrivateKey = str(value)
        else:
            raise AttributeError(
                "field '%s' not allowed in '%s' class" %
                (item, self.__class__.__name__)
            )
    __setattr__ = __setitem__

    def __getattr__(self, attr):
        _attr = dict.get(self, attr, self.__dict__.get(attr, False))
        if _attr is False:
            raise AttributeError(
                "'%s' object has no field '%s'" %
                (self.__class__.__name__, attr)
            )
        else:
            return _attr

    def setFee(self, value=None):
        """
        Set ``fee`` field manually or according to inner parameters.

        Args:
            value (:class:`int`): fee value in ``statoshi`` to set manually
        """
        self.fee = self._compute_fee(value)

    def feeIncluded(self):
        """
        Arrange ``amount`` and ``fee`` values so the total ``satoshi`` flow is
        the desired spent.
        """
        if self["type"] in [0, 7] and self["fee"] < self["amount"]:
            if "_amount" not in self.__dict__:
                self.__dict__["_amount"] = self["amount"]
            self["amount"] = self.__dict__["_amount"] - self["fee"]

    def feeExcluded(self):
        """
        Arrange ``amount`` and ``fee`` values so the total ``satoshi`` flow is
        the desired spent plus the fee.
        """
        if self["type"] in [0, 7] and "_amount" in self.__dict__:
            self["amount"] = self.__dict__["_amount"]
            self.__dict__.pop("_amount", False)

    # sign functions using passphrases
    def signWithSecret(self, secret):
        """
        Generate the ``signature`` field using passphrase. The associated
        public and private keys are stored till
        :func:`unlink` is called.

        Args:
            secret (:class:`str`): passphrase
        """
        self.link(secret)
        self.sign()

    def signSignWithSecondSecret(self, secondSecret):
        """
        Generate the ``signSignature`` field using second passphrase. The
        associated second public and private keys are stored till
        :func:`unlink` is called.

        Args:
            secondSecret (:class:`str`): second passphrase
        """
        self.link(None, secondSecret)
        self.signSign()

    def multiSignWithSecret(self, secret):
        """
        Add a signature in ``signatures`` field according to given index and
        passphrase.

        Args:
            index (:class:`int`): signature index
            secret (:class:`str`): passphrase
        """
        if self.type != 4:
            raise Exception(
                "multisignature only allowed for transaction type 4"
            )

        keys = dposlib.core.crypto.getKeys(secret)
        try:
            self.multiSignWithKey(
                self.asset["multiSignature"]["publicKeys"].index(
                    keys["publicKey"]
                ), keys["privateKey"]
            )
        except ValueError:
            raise Exception(
                "publicKey %s not allowed in this transaction" %
                keys["publicKey"]
            )

    # sign function using crypto keys
    def signWithKeys(self, publicKey, privateKey):
        """
        Generate the ``signature`` field using public and private keys. They
        are till :func:`unlink` is called.

        Args:
            publicKey (:class:`str`): public key as hex string
            privateKey (:class:`str`): private key as hex string
        """
        Transaction._publicKey = publicKey
        Transaction._privateKey = privateKey
        self.sign()

    def signSignWithKey(self, secondPrivateKey):
        """
        Generate the ``signSignature`` field using second private key. It is
        stored till :func:`unlink` is called.

        Args:
            secondPrivateKey (:class:`str`): second private key as hex string
        """
        Transaction._secondPrivateKey = secondPrivateKey
        self.signSign()

    def multiSignWithKey(self, index, privateKey):
        """
        Add a signature in ``signatures`` field according to given index and
        privateKey.

        Args:
            index (:class:`int`): signature index
            privateKey (:class:`str`): private key as hex string
        """
        if self.type != 4:
            raise Exception(
                "multisignature only allowed for transaction type 4"
            )

        self.pop("id", False)
        if "fee" not in self:
            self.setFee()
        if "signatures" not in self:
            self["signatures"] = \
                [None] * len(self.asset["multiSignature"]["publicKeys"])
        self["signatures"][index] = \
            "%02x" % index + dposlib.core.crypto.getSignature(self, privateKey)

    # root sign function called by others
    def sign(self):
        """
        Generate the ``signature`` field. Private key have to be set first. See
        :func:`link`.
        """
        if hasattr(Transaction, "_privateKey"):
            if "sendserPublicKey" not in self:
                self._setSenderPublicKey(Transaction._publicKey)
            address = dposlib.core.crypto.getAddress(Transaction._publicKey)
            if self["type"] != 4:
                self["senderId"] = address
            if self["type"] in [1, 3, 9] and "recipientId" not in self:
                self["recipientId"] = address
            if "fee" not in self:
                self.setFee()
            self["signature"] = dposlib.core.crypto.getSignature(
                self, Transaction._privateKey
            )
        else:
            raise Exception("orphan transaction can not sign itsef")

    # root second sign function called by others
    def signSign(self):
        """
        Generate the ``signSignature`` field. Transaction have to be signed and
        second  private key have to be set first. See
        :func:`link`.
        """
        if "signature" in self:
            try:
                self["signSignature"] = dposlib.core.crypto.getSignature(
                    self, Transaction._secondPrivateKey
                )
            except AttributeError:
                raise Exception("no second private Key available")
        else:
            raise Exception("transaction not signed")

    def identify(self):
        """Generate the ``id`` field. Transaction have to be signed."""
        if "signature" in self:
            self["id"] = dposlib.core.crypto.getId(self)
        else:
            raise Exception("transaction not signed")

    def finalize(self, secret=None, secondSecret=None,
                 fee=None, fee_included=False):
        """
        Finalize a transaction by setting ``fee``, signatures and ``id``.

        Args:
            secret (:class:`str`): passphrase
            secondSecret (:class:`str`): second passphrase
            fee (:class:`int`): manually set fee value in ``satoshi``
            fee_included (:class:`bool`):
                see :func:`feeIncluded`
                :func:`feeExcluded`
        """
        self.link(secret, secondSecret)
        if "fee" not in self or fee is not None:
            self["fee"] = fee
        self.feeIncluded() if fee_included else self.feeExcluded()
        self.sign()
        if hasattr(Transaction, "_secondPrivateKey"):
            self.signSign()
        self.identify()

    def dump(self):
        """Dumps transaction in registry."""
        if "id" in self:
            pathfile = Transaction.path()
            data = dict(self)
            data.pop("senderId", False)
            data.pop("signature", False)
            data.pop("signSignature", False)
            data["network"] = int(dposlib.rest.cfg.marker, base=16)
            registry = loadJson(pathfile)
            registry[data.pop("id")] = data
            dumpJson(registry, pathfile)
        else:
            raise Exception("transaction is not finalized")


# API
class Data:
    """
    This abstract class gives basic interface to json interaction within
    blockchain.
    """

    REF = set()
    EVENT = False
    TRACK = True

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
                    getattr(Transaction, "_publicKey", " ")
                ) == obj.address
            ) or (
                getattr(Transaction, "_publicKey", None) == obj.publicKey and
                getattr(
                    Transaction, "_secondPublicKey", None
                ) == obj.secondPublicKey
            ):
                return func(*args, **kw)
            else:
                raise Exception("wallet not linked yet or publicKey mismatch")
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
            return Data.__getattribute__(attr)
        except Exception:
            if attr in self.__dict:
                return self.__dict[attr]
            else:
                raise AttributeError("field '%s' can not be found" % attr)

    def _get_result(self):
        if dposlib.rest.cfg.familly == "lisk.v10":
            result = self.__endpoint(*self.__args, **self.__kwargs)
            if isinstance(result, list):
                return result[0]
            elif isinstance(result, dict):
                return result
        else:
            return self.__endpoint(*self.__args, **self.__kwargs)

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


class Wallet(Data):

    ARK_TX_VERSION = False

    ark_tx_v2 = property(
        lambda w: Wallet.ARK_TX_VERSION,
        lambda w, v: setattr(Wallet, "ARK_TX_VERSION", bool(v)),
        None,
        "Activate or deactivate transaction version 2"
    )

    unlink = staticmethod(Transaction.unlink)

    def link(self, secret=None, secondSecret=None):
        """
        """
        self.unlink()
        try:
            keys = dposlib.core.crypto.getKeys(
                secret if secret is not None else
                getpass.getpass("secret > ")
            )
            if self.publicKey is None:  # uncreated wallet
                while dposlib.core.crypto.getAddress(
                    keys.get("publicKey", None)
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
            Transaction._publicKey = keys["publicKey"]
            Transaction._privateKey = keys["privateKey"]
            if len(keys_2):
                Transaction._secondPublicKey = keys_2["publicKey"]
                Transaction._secondPrivateKey = keys_2["privateKey"]
            return True

    def setFeeLevel(self, fee_level=None):
        if fee_level is None:
            Transaction.useStaticFee()
        else:
            Transaction.useDynamicFee(fee_level)

    def _finalizeTx(self, tx, fee=None, fee_included=False):
        tx.finalize(fee=fee, fee_included=fee_included)
        return tx

    @Data.wallet_islinked
    def send(self, amount, address, vendorField=None, fee_included=False):
        tx = dposlib.core.transfer(
            amount, address, vendorField,
            version=2 if Wallet.ARK_TX_VERSION else 1
        )
        return dposlib.core.broadcastTransactions(
            self._finalizeTx(tx, fee_included=fee_included)
        )

    @Data.wallet_islinked
    def registerSecondSecret(self, secondSecret):
        tx = dposlib.core.registerSecondSecret(
            secondSecret, version=2 if Wallet.ARK_TX_VERSION else 1
        )
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @Data.wallet_islinked
    def registerSecondPublicKey(self, secondPublicKey):
        tx = dposlib.core.registerSecondPublicKey(
            secondPublicKey, version=2 if Wallet.ARK_TX_VERSION else 1
        )
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @Data.wallet_islinked
    def registerAsDelegate(self, username):
        tx = dposlib.core.registerAsDelegate(
            username, version=2 if Wallet.ARK_TX_VERSION else 1
        )
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @Data.wallet_islinked
    def upVote(self, *usernames):
        tx = dposlib.core.upVote(
            *usernames, version=2 if Wallet.ARK_TX_VERSION else 1
        )
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))

    @Data.wallet_islinked
    def downVote(self, *usernames):
        tx = dposlib.core.downVote(
            *usernames, version=2 if Wallet.ARK_TX_VERSION else 1
        )
        return dposlib.core.broadcastTransactions(self._finalizeTx(tx))
