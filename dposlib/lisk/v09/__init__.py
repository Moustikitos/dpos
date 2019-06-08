# -*- coding: utf-8 -*-
# © Toons

import os
import sys
import pytz
import dposlib

from datetime import datetime

from dposlib import rest
from dposlib.lisk import crypto
from dposlib.lisk.v09 import api
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
	"senderPublicKey": str,
	"recipientId": str,
	"senderId": str,
	"asset": dict,
	"signature": str,
	"signSignature": str,
	"id": str,
}


def select_peers():
	pass


@setInterval(30)
def rotate_peers():
	select_peers()


def init():
	Transaction.DFEES = False

	cfg.begintime = datetime(*cfg.begintime, tzinfo=pytz.UTC)
	resp = rest.GET.api.blocks.getNethash()
	if resp.get("success", False):
		cfg.hotmode = True
		cfg.headers["version"] = str(rest.GET.api.peers.version(returnKey="version"))
		cfg.headers["nethash"] = resp["nethash"]
		cfg.fees = rest.GET.api.blocks.getFees()["fees"]


def stop():
	pass


def transfer(amount, address, vendorField=None):
	return Transaction(
		type=0,
		amount=amount*100000000,
		recipientId=address,
	)

