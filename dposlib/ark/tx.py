# -*- coding: utf-8 -*-

import re
import json
import dposlib
from io import BytesIO
from collections import OrderedDict

from dposlib import cfg
from dposlib.ark import slots, serde
from dposlib.util.bin import hexlify, unhexlify, pack, pack_bytes, checkAddress


def setSenderPublicKey(cls, publicKey):
    # load information from blockchain
    address = dposlib.core.crypto.getAddress(publicKey)
    # TODO: cache data ?
    data = dposlib.rest.GET.api.wallets(address).get("data", {})
    attributes = data.get("attributes", {})
    # keep original nonce
    cls._nonce = int(data.get("nonce", 0))
    cls._multisignature = attributes.get("multiSignature", {})
    cls._secondPublicKey = attributes.get("secondPublicKey", None)
    if "nonce" not in cls:
        cls["nonce"] = cls._nonce + 1
    # add a timestamp if no one found
    if "timestamp" not in cls:
        cls["timestamp"] = slots.getTime()
    # deal with recipientId and senderId fields
    cls["senderId"] = address
    if cls["type"] not in [0, 8] and "recipientId" not in cls:
        cls["recipientId"] = address
    # add "senderPublicKey" and "_publicKey" avoiding recursion loop
    dict.__setitem__(cls, "senderPublicKey", publicKey)
    cls._publicKey = publicKey


def deleteSenderPublicKey(cls):
    cls._reset()
    del cls._nonce
    del cls._multisignature
    del cls._secondPublicKey
    del cls._publicKey

    try:
        del cls._privateKey
        del cls._secondPrivateKey
    except Exception:
        pass

    cls.pop("nonce", None)
    cls.pop("senderId", None)
    if cls["type"] not in [0, 8]:
        cls.pop("recipientId", None)
    cls.pop("senderPublicKey", None)


def setFees(cls, value=None):
    fmult = Transaction.FMULT
    feesl = Transaction.FEESL
    name = dposlib.core.GETNAME.get(
        cls["typeGroup"], 1
    ).get(cls["type"], 0)(cls)

    # manualy set fees
    if isinstance(value, (float, int)):
        value = int(value)

    else:
        # try to use fee multiplier
        try:
            fmult = int(value)
        # use fee statistics or static fees
        except (ValueError, TypeError):
            fmult = Transaction.FMULT
            if isinstance(value, str):
                feesl = value if value[:3] in ["min", "avg", "max"] else feesl
        else:
            feesl = None

        if feesl is None:
            # use static fees
            if fmult is None:
                value = int(
                    getattr(cfg, "fees", {}).get("staticFees", {})
                    .get(name, 10000000)
                )
            # compute dynamic fees
            # https://github.com/ArkEcosystem/AIPs/blob/master/AIPS/aip-16.md
            else:
                typ_ = cls.get("type", 0)
                version = cls.get("version", 0x01)

                vendorField = cls.get("vendorField", "")
                lenVF = len(
                    vendorField if isinstance(vendorField, bytes) else
                    vendorField.encode("utf-8")
                )

                value = int(
                    cfg.doffsets.get(name, 100) +
                    55 + (4 if version >= 0x02 else 0) +
                    lenVF + len(serde.serializePayload(cls))
                ) * fmult
        # use fee statistics
        else:
            value = int(cfg.feestats[str(cls["typeGroup"])][name][feesl[:3]])

    cls._reset()
    dict.__setitem__(cls, "fee", value)


def setFeeIncluded(cls):
    if cls["type"] in [0, 7] and cls["fee"] < cls["amount"]:
        cls._reset()
        if "_amount" not in cls.__dict__:
            cls._amount = cls["amount"]
        cls["amount"] = cls._amount - cls["fee"]


def unsetFeeIncluded(cls):
    if cls["type"] in [0, 7] and "_amount" in cls.__dict__:
        cls._reset()
        cls["amount"] = cls._amount
        cls.__dict__.pop("_amount", False)


def setVendorField(cls, value, encoding="utf-8"):
    if isinstance(value, bytes):
        value = value.decode(encoding)
    elif not isinstance(value, str):
        value = "%s" % value
    cls._reset()
    cls._setitem("vendorField", value)


def setVendorFieldHex(cls, value, encoding="utf-8"):
    value = value.decode(encoding) if isinstance(value, bytes) else value
    if (
        re.match(r"^[0-9a-fA-F]*$", value) is not None and
        len(value) % 2 == 0
    ):
        cls._reset()
        cls._setitem("vendorField", unhexlify(value).decode(encoding))
    else:
        raise ValueError("'%s' seems not be a valid hex string" % value)


def setTimestamp(cls, value):
    if isinstance(value, dict):
        value = value.get("epoch", slots.getTime())
    elif isinstance(value, slots.datetime):
        value = slots.getTime(value)
    cls._reset()
    cls._setitem("timestamp", value)


# Reference:
# - https://github.com/ArkEcosystem/AIPs/blob/master/AIPS/aip-11.md
def serialize(tx, **options):
    """
    Serialize transaction.

    Args:
        tx (dict or Transaction): transaction object.

    Returns:
        bytes: transaction serial representation.
    """
    buf = BytesIO()
    vendorField = tx.get("vendorField", "").encode("utf-8")[:255]
    version = tx.get("version", 1)

    # common part
    pack("<BBB", buf, (0xff, version, cfg.pubkeyHash))
    if version >= 2:
        pack("<IHQ", buf, (tx.get("typeGroup", 1), tx["type"], tx["nonce"],))
    else:
        pack("<BI", buf, (tx["type"], tx["timestamp"],))
    pack_bytes(buf, unhexlify(tx["senderPublicKey"]))
    pack("<QB", buf, (tx["fee"], len(vendorField)))
    pack_bytes(buf, vendorField)

    # custom part
    pack_bytes(buf, serde.serializePayload(tx))

    # signatures part
    if not options.get("exclude_sig", False):
        pack_bytes(buf, unhexlify(tx.get("signature", "")))
    if not options.get("exclude_second_sig", False):
        pack_bytes(buf, unhexlify(tx.get("signSignature", "")))
    if "signatures" in tx and not options.get("exclude_multi_sig", False):
        if version == 1:
            pack("<B", buf, (0xff,))
        pack_bytes(buf, b"".join([unhexlify(sig) for sig in tx["signatures"]]))

    # id part
    if "id" in tx:
        pack_bytes(buf, unhexlify(tx.get("id", "")))

    result = buf.getvalue()
    buf.close()
    return result


class Transaction(dict):
    """
    A python `dict` that implements all the necessities to manually generate
    valid transactions.
    """

    FMULT = None
    FEESL = None

    # custom properties definitions
    datetime = property(
        lambda cls: slots.getRealTime(cls["timestamp"]),
        None,
        None,
        "Transaction timestamp returned as python datetime object"
    )
    fee = property(
        lambda cls: cls.get("fee", None),
        lambda cls, value: setFees(cls, value),
        None,
    )
    vendorField = property(
        lambda cls: cls.get("vendorField", None),
        lambda cls, value: setVendorField(cls, value),
        lambda cls: setVendorField(cls, ""),
    )
    vendorFieldHex = property(
        lambda cls: hexlify(cls.get("vendorField", "").encode("utf-8")),
        lambda cls, value: setVendorFieldHex(cls, value),
        lambda cls: setVendorField(cls, ""),
    )
    timestamp = property(
        lambda cls: cls.get("timestamp", None),
        lambda cls, value: setTimestamp(cls, value),
        None,
        "Transaction timestamp setter"
    )
    recipientId = recipient = property(
        lambda cls: cls.get("recipientId", None),
        lambda cls, value: cls._setitem("recipientId", checkAddress(value)),
        lambda cls: cls.pop("recipientId", None),
        "Receiver address checker and setter"
    )
    senderId = sender = property(
        lambda cls: cls.get("senderId", None),
        lambda cls, value: cls._setitem("senderId", checkAddress(value)),
        lambda cls: cls.pop("senderId", None),
        "Sender address checker and setter"
    )
    senderPublicKey = property(
        lambda cls: cls.get("senderPublicKey", None),
        lambda cls, value: setSenderPublicKey(cls, value),
        lambda cls: deleteSenderPublicKey(cls),
        "Initialize transaction according to senderPublicKey value"
    )
    secondSignature = signSignature = property(
        lambda cls: cls.get("signSignature", None),
        lambda cls, value: cls._setitem("signSignature", value),
        lambda cls: cls.pop("signSignature", None),
        "Second signature"
    )
    #: If `True` then `amount` + `fee` = total arktoshi flow
    feeIncluded = property(
        lambda cls: "_amount" in cls.__dict__,
        lambda cls, value: (
            setFeeIncluded if bool(value) else unsetFeeIncluded
        )(cls),
        None,
        "if `True` then `amount` + `fee` = total arktoshi flow"
    )

    @staticmethod
    def useDynamicFee(value="minFee"):
        """
        Activate and configure dynamic fees parameters. Value can be either an
        integer defining the fee multiplier constant or a string defining the
        fee level to use acccording to the 30-days-average. possible values are
        `avgFee` `minFee` (default) and `maxFee`.

        Args:
            value (str or int): constant or fee multiplier.
        """
        if hasattr(cfg, "doffsets"):
            if isinstance(value, (int, float)):
                Transaction.FMULT = int(value)
                Transaction.FEESL = None
            elif value in ["maxFee", "avgFee", "minFee"]:
                Transaction.FMULT = None
                Transaction.FEESL = value
            else:
                Transaction.FMULT = None
                Transaction.FEESL = None
        else:
            Transaction.FMULT = None
            Transaction.FEESL = None

    setDynamicFee = useDynamicFee
    useStaticFee = setStaticFee = lambda self: self.useDynamicFee(None)

    # private definitions
    def _setitem(self, item, value):
        try:
            cast = dposlib.core.TYPING[item]
        except KeyError:
            dict.__setattr__(self, item, value)
        else:
            if not isinstance(value, cast):
                value = cast(value)
            dict.__setitem__(self, item, value)

    def _reset(self):
        """remove data linked to validation process."""
        self.pop("signature", False)
        self.pop("signatures", False)
        self.pop("signSignature", False)
        self.pop("secondSignature", False)
        self.pop("id", False)

    def __init__(self, *args, **kwargs):
        self._ignore_bad_fields = kwargs.pop("ignore_bad_fields", False)
        self.FEESL = kwargs.pop("FEESL", Transaction.FEESL)
        self.FMULT = kwargs.pop("FMULT", Transaction.FMULT)
        # initialize a void dict
        dict.__init__(self)
        # if blockchain package loaded merge all elements else return void dict
        data = dict(*args, **kwargs)
        last_to_be_set = [
            (k, data.pop(k, None)) for k in [
                "fee", "nonce",
                "signatures", "signature", "signSignature",
                "secondSignature", "id"
            ]
        ]
        # set default values
        dict.__setitem__(self, "version", data.pop("version", 2))
        dict.__setitem__(self, "network", getattr(cfg, "pubkeyHash", 30))
        dict.__setitem__(self, "typeGroup", data.pop("typeGroup", 1))
        dict.__setitem__(self, "amount", int(data.pop("amount", 0)))
        dict.__setitem__(self, "type", data.pop("type", 0))
        dict.__setitem__(self, "asset", data.pop("asset", {}))
        # initialize all non-void fields
        for key, value in [
            (k, v) for k, v in list(data.items()) + last_to_be_set
            if v is not None
        ]:
            if key == "fee":
                value = int(value)
            self[key] = value

    def __setitem__(self, item, value):
        if item == "secret":
            self.link(value)
        elif item == "secondSecret":
            self.link(None, value)
        else:
            try:
                dict.__getattribute__(self, item)
            except AttributeError:
                self._setitem(item, value)
            else:
                object.__setattr__(self, item, value)
    __setattr__ = __setitem__

    def __getattr__(self, attr):
        try:
            return dict.__getitem__(self, attr)
        except KeyError:
            return dict.__getattribute__(self, attr)
    __getitem__ = __getattr__

    def __str__(self):
        return json.dumps(
            OrderedDict(sorted(self.items(), key=lambda e: e[0])),
            indent=2
        )

    def __repr__(self):
        return "<Blockchain transaction type %(typeGroup)s:%(type)s>" % self

    def link(self, secret=None, secondSecret=None):
        """
        Save public and private keys derived from secrets. This is equivalent
        to wallet login. it limits number of secret keyboard entries.

        Args:
            secret (str): passphrase.
            secondSecret (str): second passphrase.
        """
        if hasattr(dposlib, "core"):
            if secret:
                keys = dposlib.core.crypto.getKeys(secret)
                self.senderPublicKey = keys["publicKey"]
                self._privateKey = keys["privateKey"]
            if secondSecret:
                keys = dposlib.core.crypto.getKeys(secondSecret)
                self._secondPrivateKey = keys["privateKey"]

    def unlink(self):
        try:
            deleteSenderPublicKey(self)
            del self._privateKey
            del self._secondPrivateKey
        except Exception:
            pass

    def touch(self):
        if hasattr(self, "_publicKey"):
            self.senderPublicKey = self._publicKey

    # root sign function called by others
    def sign(self):
        """
        Generate the `signature` field. Private key have to be set first.
        """
        self._reset()
        if hasattr(self, "_privateKey"):
            if "fee" not in self:
                setFees(self)
            if self.type == 4:
                missings = \
                    self.asset["multiSignature"]["min"] - \
                    len(self.get("signature", []))
                if missings:
                    raise Exception("owner signature missing (%d)" % missings)
            self["signature"] = dposlib.core.crypto.getSignature(
               self, self._privateKey
            )
        else:
            raise Exception("orphan transaction can not sign itsef")

    # root second sign function called by others
    def signSign(self):
        """
        Generate the `signSignature` field. Transaction have to be signed and
        second private key have to be set first.
        """
        if "signature" in self:  # or "signatures" in self ?
            self.pop("id", False)
            try:
                self["signSignature"] = dposlib.core.crypto.getSignature(
                    self, self._secondPrivateKey,
                    exclude_second_sig=True,
                )
            except AttributeError:
                raise Exception("no second private Key available")
        else:
            raise Exception("transaction not signed")

    # sign functions using passphrases
    def signWithSecret(self, secret):
        """
        Generate the `signature` field using passphrase. The associated
        public and private keys are stored till `dposlib.ark.unlink` is called.

        Args:
            secret (`str`): passphrase.
        """
        self.link(secret)
        self.sign()

    def signSignWithSecondSecret(self, secondSecret):
        """
        Generate the `signSignature` field using second passphrase. The
        associated second public and private keys are stored till
        `dposlib.ark.unlink` is called.

        Args:
            secondSecret (`str`): second passphrase.
        """
        self.link(None, secondSecret)
        self.signSign()

    def multiSignWithSecret(self, secret):
        """
        Add a signature in `signatures` field.

        Args:
            index (int): signature index.
            secret (str): passphrase.
        """
        keys = dposlib.core.crypto.getKeys(secret)
        self.multiSignWithKey(keys["privateKey"])

    # sign function using crypto keys
    def signWithKeys(self, publicKey, privateKey):
        """
        Generate the `signature` field using public and private keys. They
        are stored till `dposlib.ark.unlink` is called.

        Args:
            publicKey (str): public key as hex string.
            privateKey (str): private key as hex string.
        """
        if self.get("senderPublicKey", None) != publicKey:
            self.senderPublicKey = publicKey
        self._privateKey = privateKey
        self.sign()

    def signSignWithKey(self, secondPrivateKey):
        """
        Generate the `signSignature` field using second private key. It is
        stored till `dposlib.ark.unlink` is called.

        Args:
            secondPrivateKey (`str`): second private key as hex string.
        """
        self._secondPrivateKey = secondPrivateKey
        self.signSign()

    def multiSignWithKey(self, privateKey):
        """
        Add a signature in `signatures` field according to given index and
        privateKey.

        Args:
            privateKey (str): private key as hex string.
        """
        # remove id if any and set fee if needed
        self.pop("id", False)
        if "fee" not in self:
            setFees(self)
        # get public key from private key
        publicKey = dposlib.core.crypto.secp256k1.PublicKey.from_seed(
            unhexlify(privateKey)
        )
        publicKey = hexlify(publicKey.encode())
        # create a multi-signature
        signature = dposlib.core.crypto.getSignatureFromBytes(
            serialize(
                self,
                exclude_sig=True,
                exclude_multi_sig=True,
                exclude_second_sig=True
            ),
            privateKey
        )
        # add multisignature in transaction
        try:
            self.appendMultiSignature(publicKey, signature)
        except Exception:
            raise ValueError("public key %s not allowed here" % publicKey)

    def appendMultiSignature(self, publicKey, signature):
        # if type 4 find index in asset
        if self["type"] == 4:
            index = self.asset["multiSignature"]["publicKeys"].index(
                publicKey
            )
        # else find it in _multisignature attribute
        elif self._multisignature:
            index = self._multisignature["publicKeys"].index(publicKey)
        else:
            raise Exception("multisignature not to be used here")
        # concatenate index and signature and fill it in signatures field
        # sorted(set([...])) returns sorted([...]) with unique values
        self["signatures"] = sorted(
            set(self.get("signatures", []) + ["%02x" % index + signature]),
            key=lambda s: s[:2]
        )

    def identify(self):
        """Generate the `id` field. Transaction have to be signed."""
        if "signature" in self or "signatures" in self:
            if len(self._multisignature):
                missings = \
                    self._multisignature["min"] - \
                    len(self.get("signatures", []))
                if missings:
                    raise Exception("owner signature missing (%d)" % missings)
            elif self._secondPublicKey:
                if "signSignature" not in self:
                    raise Exception("second signature is missing")
            self.pop("id", False)
            self["id"] = dposlib.core.crypto.getIdFromBytes(
                serialize(self, exclude_multi_sig=False)
            )
        else:
            raise Exception("transaction not signed")

    def finalize(self, secret=None, secondSecret=None,
                 fee=None, fee_included=False):
        """
        Finalize a transaction by setting `fee`, signatures and `id`.

        Args:
            secret (str): passphrase.
            secondSecret (str): second passphrase.
            fee (int): manually set fee value in `arktoshi`.
            fee_included (bool): see `dposlib.ark.tx.Transaction.feeIncluded`.
        """
        self.link(secret, secondSecret)
        # automatically set fees if needed
        if "fee" not in self or fee is not None:
            self.fee = fee
        self.feeIncluded = fee_included
        # sign with private keys
        # if transaction is not from a multisignature wallet
        if not self._multisignature:
            self.sign()
            if hasattr(self, "_secondPrivateKey"):
                self.signSign()
        # generate the id
        self.identify()
