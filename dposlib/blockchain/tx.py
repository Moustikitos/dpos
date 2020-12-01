# -*- coding: utf-8 -*-
# © Toons

import re
import json
import base58
import dposlib

from collections import OrderedDict
from dposlib import BytesIO
from dposlib.blockchain import slots, cfg
from dposlib.util.bin import hexlify, unhexlify, pack, pack_bytes, checkAddress

if dposlib.PY3:
    long = int


def setDynamicFee(cls, value):
    if isinstance(value, (float, int, long)):
        fee = value
    else:
        static_value = getattr(cfg, "fees", {})\
            .get("staticFees", getattr(cfg, "fees", {}))\
            .get(dposlib.core.TRANSACTIONS[cls["type"]], 10000000)
        feesl = value if isinstance(value, str) else cls.FMULT
        # use fee statistics if FEESL is not None
        if feesl is not None:  # and cls["type"] not in [6, ]:
            # if fee statistics not found, return static fee value
            fee = cfg.feestats.get(cls["type"], {}).get(feesl, static_value)
        # else compute fees using fee multiplier and cls size
        else:
            try:
                fee = computeDynamicFees(cls, cls.FMULT)
            except Exception:
                fee = static_value
    dict.__setitem__(cls, "fee", long(fee))


def computeDynamicFees(tx, FMULT=None):
    """
    Compute transaction fees according to
    `AIP 16 <https://github.com/ArkEcosystem/AIPs/blob/master/AIPS/aip-16.md>`_

    Arguments:
        tx (:class:`dict` or :class:`Transaction`): transaction object
    Returns:
        :class:`int`: fees
    """
    typ_ = tx.get("type", 0)
    version = tx.get("version", 0x01)

    vendorField = tx.get("vendorField", "")
    vendorField = \
        vendorField if isinstance(vendorField, bytes) else \
        vendorField.encode("utf-8")
    lenVF = len(vendorField)
    payload = serializePayload(tx)
    T = cfg.doffsets.get(dposlib.core.TRANSACTIONS[typ_], 0)
    return int(
        (T + 55 + (4 if version >= 0x02 else 0) + lenVF + len(payload)) * FMULT
    )


def setSenderPublicKey(cls, publicKey):
    # load information from blockchain
    address = dposlib.core.crypto.getAddress(publicKey)
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
    if cls["type"] != 4:
        cls["senderId"] = address
    if cls["type"] in [1, 3, 6, 9] and "recipientId" not in cls:
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
    cls.pop("nonce", None)
    if cls["type"] != 4:
        cls.pop("senderId", None)
    if cls["type"] in [1, 3, 6, 9]:
        cls.pop("recipientId", None)
    cls.pop("senderPublicKey", None)


def setFeeIncluded(cls):
    """
    Arrange ``amount`` and ``fee`` values so the total ``arktoshi`` flow is
    the desired spent.
    """
    if cls["type"] in [0, 7] and cls["fee"] < cls["amount"]:
        if "_amount" not in cls.__dict__:
            cls._amount = cls["amount"]
        cls["amount"] = cls._amount - cls["fee"]
    cls._reset()


def unsetFeeIncluded(cls):
    """
    Arrange ``amount`` and ``fee`` values so the total ``arktoshi`` flow is
    the desired spent plus the fee.
    """
    if cls["type"] in [0, 7] and "_amount" in cls.__dict__:
        cls["amount"] = cls._amount
        cls.__dict__.pop("_amount", False)
    cls._reset()


def setVendorField(cls, value, encoding="utf-8"):
    if isinstance(value, bytes):
        value = value.decode(encoding)
    elif not isinstance(value, str):
        value = "%s" % value
    cls._setitem("vendorField", value)
    cls._reset()


def setVendorFieldHex(cls, value, encoding="utf-8"):
    value = value.decode(encoding) if isinstance(value, bytes) else value
    if (
        re.match(r"^[0-9a-fA-F]*$", value) is not None and
        len(value) % 2 == 0
    ):
        cls._setitem("vendorField", unhexlify(value).decode(encoding))
        cls._reset()
    else:
        raise ValueError("'%s' seems not be a valid hex string" % value)


def setTimestamp(cls, value):
    if isinstance(value, dict):
        value = value.get("epoch", slots.getTime())
    elif isinstance(value, slots.datetime):
        value = slots.getTime(value)
    cls._setitem("timestamp", value)
    cls._reset()


class Transaction(dict):
    """
    A python :class:`dict` that implements all the necessities to manually
    generate valid transactions.
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
        lambda cls, value: cls.setFee(value),
        None,
        ""
    )
    vendorField = property(
        lambda cls: cls.get("vendorField", None),
        lambda cls, value: setVendorField(cls, value),
        lambda cls: setVendorField(cls, ""),
        ""
    )
    vendorFieldHex = property(
        lambda cls: hexlify(cls.get("vendorField", "").encode("utf-8")),
        lambda cls, value: setVendorFieldHex(cls, value),
        lambda cls: setVendorField(cls, ""),
        ""
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
    feeIncluded = property(
        lambda cls: "_amount" in cls.__dict__,
        lambda cls, value: (
            setFeeIncluded if bool(value) else unsetFeeIncluded
        )(cls),
        None,
        "if `True` then :attr:`amount` + :attr:`fee` = total arktoshi flow"
    )

    @staticmethod
    def useDynamicFee(value="minFee"):
        """
        Activate and configure dynamic fees parameters. Value can be either an
        integer defining the fee multiplier constant or a string defining the
        fee level to use acccording to the 30-days-average. possible values are
        ``avgFee`` ``minFee`` (default) and ``maxFee``.

        Args:
            value (:class:`str` or :class:`int`): constant or fee multiplier
        """
        if hasattr(cfg, "doffsets"):
            if isinstance(value, (int, float, long)):
                Transaction.FMULT = long(value)
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
        """remove data linked to validation proces."""
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
        if hasattr(dposlib, "core"):
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
            dict.__setitem__(self, "amount", data.pop("amount", 0))
            dict.__setitem__(self, "type", data.pop("type", 0))
            dict.__setitem__(self, "asset", data.pop("asset", {}))
            # initialize all non-void fields
            for key, value in [
                (k, v) for k, v in list(data.items()) + last_to_be_set
                if v is not None
            ]:
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
            return dict.__getattribute__(self, attr)
        except AttributeError:
            return dict.__getitem__(self, attr)
    __getitem__ = __getattr__

    def __str__(self):
        return json.dumps(
            OrderedDict(sorted(self.items(), key=lambda e: e[0]))
        )

    def __repr__(self):
        return json.dumps(
            OrderedDict(sorted(self.items(), key=lambda e: e[0])), indent=2
        )

    def link(self, secret=None, secondSecret=None):
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

    def setFee(self, value=None):
        """
        Set ``fee`` field manually or according to inner parameters.

        Args:
            value (:class:`int`): fee value in ``statoshi`` to set manually
        """
        setDynamicFee(self, value or self.FEESL)
        self._reset()

    # root sign function called by others
    def sign(self):
        """
        Generate the ``signature`` field. Private key have to be set first. See
        :func:`link`.
        """
        self._reset()
        if hasattr(self, "_privateKey"):
            if "fee" not in self:
                self.setFee()
            if self.type == 4:
                missings = \
                    self.asset["multiSignature"]["min"] - \
                    len(self.get("signature", []))
                if missings:
                    raise Exception("owner signature missing (%d)" % missings)
            self["signature"] = dposlib.core.crypto.getSignatureFromBytes(
                serialize(self), self._privateKey
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
        if "signature" in self:  # or "signatures" in self ?
            try:
                self["signSignature"] = \
                    dposlib.core.crypto.getSignatureFromBytes(
                        serialize(self), self._secondPrivateKey
                    )
            except AttributeError:
                raise Exception("no second private Key available")
        else:
            raise Exception("transaction not signed")

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
        Add a signature in ``signatures`` field.

        Args:
            index (:class:`int`): signature index
            secret (:class:`str`): passphrase
        """
        keys = dposlib.core.crypto.getKeys(secret)
        self.multiSignWithKey(keys["privateKey"])

    # sign function using crypto keys
    def signWithKeys(self, publicKey, privateKey):
        """
        Generate the ``signature`` field using public and private keys. They
        are till :func:`unlink` is called.

        Args:
            publicKey (:class:`str`): public key as hex string
            privateKey (:class:`str`): private key as hex string
        """
        if self.get("senderPublicKey", None) != publicKey:
            self.senderPublicKey = publicKey
        self._privateKey = privateKey
        self.sign()

    def signSignWithKey(self, secondPrivateKey):
        """
        Generate the ``signSignature`` field using second private key. It is
        stored till :func:`unlink` is called.

        Args:
            secondPrivateKey (:class:`str`): second private key as hex string
        """
        self._secondPrivateKey = secondPrivateKey
        self.signSign()

    def multiSignWithKey(self, privateKey):
        """
        Add a signature in ``signatures`` field according to given index and
        privateKey.

        Args:
            privateKey (:class:`str`): private key as hex string
        """
        # get public key from private key
        publicKey = dposlib.core.crypto.secp256k1.PublicKey.from_seed(
            unhexlify(privateKey)
        )
        publicKey = hexlify(publicKey.encode())

        # get public key index :
        # if type 4 find index in asset
        # else find it in _multisignature attribute
        if self["type"] == 4:
            index = self.asset["multiSignature"]["publicKeys"].index(
                publicKey
            )
        elif self._multisignature:
            if publicKey not in self._multisignature["publicKeys"]:
                raise ValueError("public key %s not allowed here" % publicKey)
            index = self._multisignature["publicKeys"].index(publicKey)
        else:
            raise Exception("multisignature not to be used here")

        # remove id if any and set fee
        self.pop("id", False)
        if "fee" not in self:
            self.setFee()

        # concatenate index and signature and fill it in signatures field
        # sorted(set([...])) returns sorted([...]) with unique values
        self["signatures"] = sorted(set(
            self.get("signatures", []) + [
                "%02x" % index +
                dposlib.core.crypto.getSignatureFromBytes(
                    serialize(
                        self,
                        exclude_sig=True,
                        exclude_multi_sig=True,
                        exclude_second_sig=True
                    ),
                    privateKey
                )
            ]),
            key=lambda s: s[:2]
        )

    def identify(self):
        """Generate the ``id`` field. Transaction have to be signed."""
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
            self["id"] = dposlib.core.crypto.getIdFromBytes(
                serialize(self, exclude_multi_sig=False)
            )
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
                see :attr:`Transaction.feeIncluded`
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


# Reference:
# - https://github.com/ArkEcosystem/AIPs/blob/master/AIPS/aip-11.md
# - https://github.com/ArkEcosystem/AIPs/blob/master/AIPS/aip-102.md
def serialize(tx, **options):
    """
    Serialize transaction.

    Args:
        tx (:class:`dict` or :class:`Transaction`):
            transaction object

    Returns:
        :class:`bytes`: bytes sequence
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
    pack_bytes(buf, serializePayload(tx))

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
    pack_bytes(buf, unhexlify(tx.get("id", "")))

    result = buf.getvalue()
    buf.close()
    return result


def serializePayload(tx):
    asset = tx.get("asset", {})
    buf = BytesIO()
    _type = tx["type"]

    # transfer transaction
    if _type == 0:
        try:
            recipientId = str(tx["recipientId"]) if not isinstance(
                    tx["recipientId"], bytes
                ) else \
                tx["recipientId"]
            recipientId = base58.b58decode_check(recipientId)
        except Exception:
            raise Exception("no recipientId defined")
        pack("<QI", buf, (
            int(tx.get("amount", 0)),
            int(tx.get("expiration", 0)),
        ))
        pack_bytes(buf, recipientId)

    # secondSignature registration
    elif _type == 1:
        if "signature" in asset:
            secondPublicKey = asset["signature"]["publicKey"]
        else:
            raise Exception("no secondSecret or secondPublicKey given")
        pack_bytes(buf, unhexlify(secondPublicKey))

    # delegate registration
    elif _type == 2:
        username = asset.get("delegate", {}).get("username", False)
        if username:
            length = len(username)
            if 3 <= length <= 255:
                pack("<B", buf, (length, ))
                pack_bytes(buf, username.encode("utf-8"))
            else:
                raise Exception("bad username length [3-255]: %s" % username)
        else:
            raise Exception("no username defined")

    # vote
    elif _type == 3:
        delegatePublicKeys = asset.get("votes", False)
        if delegatePublicKeys:
            pack("<B", buf, (len(delegatePublicKeys), ))
            for delegatePublicKey in delegatePublicKeys:
                delegatePublicKey = delegatePublicKey.replace("+", "01")\
                                    .replace("-", "00")
                pack_bytes(buf, unhexlify(delegatePublicKey))
        else:
            raise Exception("no up/down vote given")

    # Multisignature registration
    elif _type == 4:
        multiSignature = asset.get("multiSignature", False)
        if multiSignature:
            pack(
                "<BB", buf,
                (multiSignature["min"], len(multiSignature["publicKeys"]))
            )
            pack_bytes(
                buf, b"".join(
                    [unhexlify(sig) for sig in multiSignature["publicKeys"]]
                )
            )

    # IPFS
    elif _type == 5:
        try:
            ipfs = str(asset["ipfs"]) if not isinstance(
                    asset["ipfs"], bytes
                ) else asset["ipfs"]
            data = base58.b58decode(ipfs)
        except Exception as e:
            raise Exception("bad ipfs autentification\n%r" % e)
        pack_bytes(buf, data)

    # multipayment
    elif _type == 6:
        try:
            items = [
                (p["amount"], base58.b58decode_check(
                    str(p["recipientId"]) if not isinstance(
                        p["recipientId"], bytes
                    ) else p["recipientId"]
                )) for p in asset.get("payments", {})
            ]
        except Exception:
            raise Exception("error in recipientId address list")
        result = pack("<H", buf, (len(items), ))
        for amount, address in items:
            pack("<Q", buf, (amount, ))
            pack_bytes(buf, address)

    # delegate resignation
    elif _type == 7:
        pass

    # HTLC lock
    elif _type == 8:
        try:
            recipientId = str(tx["recipientId"]) if not isinstance(
                tx["recipientId"], bytes
            ) else tx["recipientId"]
            recipientId = base58.b58decode_check(recipientId)
        except Exception:
            raise Exception("no recipientId defined")
        lock = asset.get("lock", False)
        expiration = lock.get("expiration", False)
        if not lock or not expiration:
            raise Exception("no lock nor expiration data found")
        pack("<Q", buf, (int(tx.get("amount", 0)),))
        pack_bytes(buf, unhexlify(lock["secretHash"]))
        pack("<BI", buf, [int(expiration["type"]), int(expiration["value"])])
        pack_bytes(buf, recipientId)

    # HTLC claim
    elif _type == 9:
        claim = asset.get("claim", False)
        if not claim:
            raise Exception("no claim data found")
        pack_bytes(buf, unhexlify(claim["lockTransactionId"]))
        pack_bytes(buf, claim["unlockSecret"].encode("utf-8"))

    # HTLC refund
    elif _type == 10:
        refund = asset.get("refund", False)
        if not refund:
            raise Exception("no refund data found")
        pack_bytes(buf, unhexlify(refund["lockTransactionId"]))

    else:
        raise Exception("Unknown transaction type %d" % tx["type"])

    result = buf.getvalue()
    buf.close()
    return result
