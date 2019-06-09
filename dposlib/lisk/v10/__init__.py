# -*- coding: utf-8 -*-
# © Toons

import os
import sys
import pytz
import dposlib

from datetime import datetime

from dposlib import rest
from dposlib.lisk import crypto
from dposlib.lisk.v10 import api
from dposlib.blockchain import cfg, slots, Transaction
from dposlib.util.asynch import setInterval
from dposlib.util.data import loadJson, dumpJson


TRANSACTIONS = {
	0: "send",
	1: "secondsignature",
	2: "delegate",
	3: "vote",
}
TYPING = {
	"timestamp": int,
	"type": int,
	"amount": str,
	"fee": str,
	"senderPublicKey": str,
	"recipientId": str,
	"senderId": str,
	"asset": dict,
	"signature": str,
	"signSignature": str,
	"id": str,
}


def init():
	Transaction.DFEES = False

	if len(cfg.peers):
		constants = rest.GET.api.node.constants().get("data", {})
		cfg.hotmode = True
		dumpJson(constants, os.path.join(dposlib.ROOT, ".cold", cfg.network+".cfg"))
	else:
		cfg.hotmode = False
		constants = loadJson(os.path.join(dposlib.ROOT, ".cold", cfg.network+".cfg"))

	if len(constants):
		cfg.begintime = pytz.utc.localize(datetime.strptime(constants["epoch"], "%Y-%m-%dT%H:%M:00.000Z"))
		cfg.headers["nethash"] = constants["nethash"]
		cfg.headers["version"] = str(constants["version"])
		cfg.fees = constants["fees"]
		cfg.blockreward = int(constants["reward"]) / 100000000.


def stop():
	pass


def broadcastTransactions(*transactions, **params):
	chunk_size = params.pop("chunk_size", 20)

	report = []
	for chunk in [transactions[i:i+chunk_size] for i in range(0, len(transactions), chunk_size)]:
		response = rest.POST.api.transactions(transactions=chunk)
		response["ids"] = [tx["id"] for tx in chunk]
		report.append(response)

	return None if len(report) == 0 else \
		   report[0] if len(report) == 1 else \
		   report


def transfer(amount, address, vendorField=None):
	return Transaction(
		type=0,
		amount=amount*100000000,
		recipientId=address,
	)


def registerSecondSecret(secondSecret):
	raise NotImplementedError("Transaction not implemented yet")


def registerSecondPublicKey(secondPublicKey):
	raise NotImplementedError("Transaction not implemented yet")


def registerAsDelegate(username):
	raise NotImplementedError("Transaction not implemented yet")


def upVote(*usernames):
	raise NotImplementedError("Transaction not implemented yet")


def downVote(*usernames):
	raise NotImplementedError("Transaction not implemented yet")

