# -*- coding: utf-8 -*-
# © Toons

"""
This module contains functions to interoperate with Ledger Nano S.
"""

import io
import os
import struct

import dposlib
import ledgerblue
from dposlib.util.bin import unhexlify, hexlify, intasb, basint
from ledgerblue.comm import getDongle

PACK = (lambda f, v: struct.pack(f, v)) if dposlib.PY3 else \
       (lambda f, v: bytes(struct.pack(f, v)))


def parseBip32Path(path):
	"""
	Parse a derivation path.
	~https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki

	Argument:
	path -- the derivation path

	Return bytes
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


def buildTxApdu(dongle_path, data):
	"""
	Generate apdu from data. This apdu is to be sent into the ledger key.

	Argument:
	dongle_path -- value returned by parseBip32Path
	data -- bytes value returned by dposlib.core.crypto.getBytes

	Return bytes
	"""

	path_len = len(dongle_path)

	if len(data) > 255 - (path_len+1):
		data1 = data[:255-(path_len+1)]
		data2 = data[255-(path_len+1):]
		p1 = unhexlify("e0040040")
	else:
		data1 = data
		data2 = unhexlify("")
		p1 = unhexlify("e0048040")

	return [
		p1 + intasb(1 + path_len + len(data1)) + intasb(path_len//4) + dongle_path + data1,
		unhexlify("e0048140") + intasb(len(data2)) + data2 if len(data2) else None
	]


def buildPkeyApdu(dongle_path):
	"""
	Generate apdu to get public key from ledger key.

	Argument:
	dongle_path -- value returned by parseBip32Path

	Return bytes
	"""

	path_len = len(dongle_path)
	return unhexlify("e0020040") + intasb(1 + path_len) + \
	       intasb(path_len//4) + dongle_path


def getPublicKey(dongle_path, debug=False):
	"""
	Compute the public key associated to a derivation path.

	Argument:
	dongle_path -- value returned by parseBip32Path

	Keyword argument:
	debug -- flag to activate debug messages from ledger key [default: False]

	Return str (hex)
	"""

	apdu = buildPkeyApdu(dongle_path)
	dongle = getDongle(debug)
	data = bytes(dongle.exchange(apdu, timeout=30))
	dongle.close()
	len_pkey = basint(data[0])
	return hexlify(data[1:len_pkey+1])


def getSignature(data, dongle_path, debug=False):
	"""
	Get ledger Nano S signature of given transaction.

	Argument:
	data -- transaction as bytes data returned by dposlib.core.crypto.getBytes
	dongle_path -- value returned by parseBip32Path

	Keyword argument:
	debug -- flag to activate debug messages from ledger key [default: False]

	Return str (hex)
	"""

	apdu1, apdu2 = buildTxApdu(dongle_path, data)
	dongle = getDongle(debug)
	result = dongle.exchange(bytes(apdu1), timeout=30)
	if apdu2:
		apdu = unhexlify("e0048140") + intasb(len(apdu2)) + apdu2
		result = dongle.exchange(bytes(apdu), timeout=30)
	dongle.close()
	return hexlify(result)


def signTransaction(tx, path, debug=False):
	"""
	Append signature into transaction according to derivation path.

	Argument:
	tx -- transaction as dictionary
	path -- derivation path

	Keyword argument:
	debug -- flag to activate debug messages from ledger key [default: False]
	
	Return None
	"""

	dongle_path = parseBip32Path(path)
	tx["senderPublicKey"] = getPublicKey(dongle_path, debug)
	tx["signature"] = getSignature(dposlib.core.crypto.getBytes(tx), dongle_path, debug)
