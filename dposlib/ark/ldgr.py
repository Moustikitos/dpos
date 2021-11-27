# -*- coding: utf-8 -*-

"""
This module contains functions to interoperate with [Ledger](
    https://ledger.com
) hard wallet.
"""

import sys
import struct
import dposlib

from dposlib.util.bin import unhexlify, hexlify, intasb
from dposlib.ark.tx import serialize, Transaction
from ledgerblue.comm import getDongle
from ledgerblue.commException import CommException

PACK = (lambda f, v: struct.pack(f, v))

# Limits
chunkSize = 255
chunkMax = 10
payloadMax = chunkMax * chunkSize
# Instruction Class
cla = "e0"
# Instructions
op_puk = "02"
op_sign_tx = "04"
op_sign_msg = "08"
# PublicKey APDU P1 & P2
p1_non_confirm = "00"
p2_no_chaincode = "00"
# Signing APDU P1
p1_single = "80"
p1_first = "00"
p1_more = "01"
p1_last = "81"
# Signing Flags P2
p2_ecdsa = "40"
p2_schnorr_leg = "50"


def _default_path():
    return "44'/%s'/%s'/0/0" % (
        getattr(dposlib.rest.cfg, "slip44", "111"),
        getattr(dposlib.rest.cfg, "aip20", "0"),
    )


def parseBip44Path(path):
    """
    Parse a [BIP44](
        https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki
    ) derivation path.

    Args:
        path (str): the derivation path.

    Returns:
        bytes: parsed bip44 path.
    """
    if len(path) == 0:
        return b""
    result = b""
    elements = path.split('/')
    for pathElement in elements:
        element = pathElement.split("'")
        if len(element) == 1:
            result = result + PACK(">I", int(element[0]))
        else:
            result = result + PACK(">I", 0x80000000 | int(element[0]))
    return result


def splitData(data, dongle_path):
    first = chunkSize - len(dongle_path) - 1
    return [
        data[:first]
    ] + [
        data[i:i + chunkSize]
        for i in range(first, len(data), chunkSize)
    ]


def buildPukApdu(dongle_path):
    path_len = len(dongle_path)
    return \
        unhexlify(cla + op_puk + p1_non_confirm + p2_no_chaincode) + \
        intasb(path_len + 1) + \
        intasb(path_len // 4) + \
        dongle_path


def buildSignatureApdu(data, dongle_path, what="tx", schnorr=True):
    apdu = []
    path_len = len(dongle_path)
    payload = len(data) + len(dongle_path) + 1

    if payload > payloadMax:
        raise CommException(
            'Payload size:', payload,
            'exceeds max length:', payloadMax
        )

    data = splitData(data, dongle_path)
    if len(data) == 1:
        first, body, last = data[0], [], None
    else:
        first, body, last = data[0], data[1:-1], data[-1]

    p2 = p2_schnorr_leg if schnorr else p2_ecdsa
    p1 = p1_single if last is None else p1_first
    op = getattr(sys.modules[__name__], "op_sign_" + what)

    apdu.append(
        unhexlify(cla + op + p1 + p2) +
        intasb(path_len + 1 + len(first)) + intasb(path_len // 4) +
        dongle_path +
        first
    )

    for b in body:
        apdu.append(
            unhexlify(cla + op + p1_more + p2) +
            intasb(len(b)) + b
        )

    if last is not None:
        apdu.append(
            unhexlify(cla + op + p1_last + p2) +
            intasb(len(last)) + last
        )

    return apdu


def sendApdu(apdus, debug=True):
    dongle = getDongle(debug)
    try:
        for apdu in apdus:
            data = bytes(dongle.exchange(apdu, timeout=30))
    except CommException as comm:
        if comm.sw == 0x6985:
            sys.stdout.write("Rejected by user\n")
        elif comm.sw in [0x6D00, 0x6F00, 0x6700]:
            sys.stdout.write(
                "Make sure your Ledger is connected and unlocked "
                "with the ARK app opened\n"
            )
        else:
            sys.stdout.write("%r\n" % comm)
        data = b""
    finally:
        dongle.close()
    return hexlify(data)


def getPublicKey(path=None, debug=False):
    """
    Compute the public key associated to a derivation path.

    Args:
        path (str): derivation path.
        debug (bool): flag to activate debug messages from ledger key.

    Returns:
        hex: secp256k1-compressed publicKey.
    """
    path = _default_path() if path is None else path
    return sendApdu([buildPukApdu(parseBip44Path(path))], debug=debug)[2:]


def signMessage(msg, path=None, schnorr=True, debug=False):
    """
    Compute schnorr or ecdsa signature of msg according to derivation path.

    Args:
        msg (str or bytes): message to sign.
        path (str): derivation path.
        schnorr (bool): use schnorr signature if True else ecdsa.
        debug (bool): flag to activate debug messages from ledger key.

    Returns:
        hex: message signature.
    """
    path = _default_path() if path is None else path
    if not isinstance(msg, bytes):
        msg = msg.encode("ascii", errors="replace")
    msg = msg.decode("ascii").encode("utf-8")
    if len(msg) > 255:
        raise ValueError("message max length is 255, got %d" % len(msg))

    return sendApdu(
        buildSignatureApdu(msg, parseBip44Path(path), "msg", schnorr),
        debug=debug
    )


def signTransaction(tx, path=None, schnorr=True, debug=False):
    """
    Append sender public key and signature into transaction according to
    derivation path.

    Args:
        tx (dposlib.ark.tx.Transaction): transaction.
        path (str): derivation path.
        schnorr (bool): use schnorr signature if True else ecdsa.
        debug (bool): flag to activate debug messages from ledger key.

    Returns:
        hex: transaction signature. Signature is also added to transaction
            object as `signature` item.
    """
    if not isinstance(tx, Transaction):
        raise ValueError(
            "tx should be %s class, get %s instead" % (
                Transaction, type(tx)
            )
        )

    path = _default_path() if path is None else path
    dongle_path = parseBip44Path(path)
    tx["senderPublicKey"] = sendApdu(
        [buildPukApdu(dongle_path)], debug=debug
    )[2:]
    tx["signature"] = sendApdu(
        buildSignatureApdu(serialize(tx), dongle_path, "tx", schnorr),
        debug=debug
    )

    return tx["signature"]
