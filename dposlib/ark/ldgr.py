# -*- coding: utf-8 -*-
# © Toons

"""
This module contains functions to interoperate with Ledger Nano S.
"""

import sys
import struct
import dposlib

from dposlib.util.bin import unhexlify, hexlify, intasb
from dposlib.blockchain.tx import serialize, Transaction
from ledgerblue.comm import getDongle
from ledgerblue.commException import CommException


PACK = (lambda f, v: struct.pack(f, v)) if dposlib.PY3 else \
       (lambda f, v: bytes(struct.pack(f, v)))


# https://github.com/sleepdefic1t/hardware-sdk-ledger/blob/master/packages/ledger-app-ark/examples/example_helper.py
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


def parseBip32Path(path="44'/111'/0'/0/0"):
    """
    Parse a BIP44 derivation path.
    https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki

    Args:
        path (str): the derivation path
    Returns:
        parsed bip32 path
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
    """
    Generate apdu to get public key from ledger key.

    Args:
        dongle_path (bytes): value returned by
                             `dposlib.ark.ldgr.parseBip32Path`
    Returns:
        :class:`bytes`: public key apdu data
    """
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

    print(first, body, last)

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
                "Make sure your Ledger is connected and unlocked",
                "with the ARK app opened\n"
            )
        data = b""
    finally:
        dongle.close()
    return hexlify(data)


def getPublicKey(dongle_path, debug=False):
    """
    Compute the public key associated to a derivation path.

    Args:
        dongle_path (bytes): value returned by
                             `dposlib.ark.ldgr.parseBip32Path`
        debug (bool): flag to activate debug messages from ledger key
                      [default: False]
    Returns:
        hexadecimal compressed publicKey
    """
    dongle = getDongle(debug)
    data = bytes(dongle.exchange(buildPukApdu(dongle_path), timeout=30))
    dongle.close()
    return hexlify(data[1:])


def signMessage(msg, path, schnorr=True, debug=False):
    if not isinstance(msg, bytes):
        msg = \
            msg.encode("ascii", errors="replace")\
            .decode("ascii").encode("utf-8")
    if len(msg) > 255:
        raise ValueError("message max length is 255, got %d" % len(msg))

    return sendApdu(
        buildSignatureApdu(msg, parseBip32Path(path), "msg", schnorr),
        debug=debug
    )


def signTransaction(tx, path, schnorr=True, debug=False):
    """
    Append sender public key and signature into transaction according to
    derivation path.

    Arguments:
        tx (dict): transaction as dictionary
        path (str): derivation path
        schnorr (bool): use schnorr signature if True else ecdsa
        debug (bool): flag to activate debug messages from ledger key
    """
    if not isinstance(tx, Transaction):
        raise ValueError(
            "tx should be %s class, get %s instead" % (
                Transaction, type(tx)
            )
        )

    dongle_path = parseBip32Path(path)
    tx["senderublicKey"] = sendApdu([buildPukApdu(dongle_path)], debug=debug)
    tx["signature"] = sendApdu(
        buildSignatureApdu(serialize(tx), dongle_path, "tx", schnorr),
        debug=debug
    )
