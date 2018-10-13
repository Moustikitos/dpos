# -*- coding: utf-8 -*-
# © Toons

import sys
import pytz

from datetime import datetime

from dposlib import rest
from dposlib.lisk import crypto
# from dposlib.lisk.v10 import api
from dposlib.blockchain import cfg, slots, Transaction
from dposlib.util.asynch import setInterval


DAEMON_PEERS = None
TRANSACTIONS = {
	0: "send",
	1: "secondsignature",
	2: "delegate",
	3: "vote",
	# 4: "multisignature",
}
TYPING = {
	"timestamp": int,
	"type": int,
	"amount": str,
	"senderPublicKey": str,
	"recipientId": str,
	"senderId": str,
	"vendorField": str,
	"asset": dict,
	"signature": str,
	"signSignature": str,
	"id": str,
}


def select_peers():
	selection = []
	for seed in cfg.seeds:
		if rest.check_latency(seed):
			selection.append(seed)

	if len(selection):
		cfg.peers = selection


@setInterval(30)
def rotate_peers():
	select_peers()


def init():
	global DAEMON_PEERS
	Transaction.DFEES = False

	constants = rest.GET.api.node.constants(returnKey="data")
	cfg.begintime = pytz.utc.localize(datetime.strptime(constants["epoch"], "%Y-%m-%dT%H:%M:00.000Z"))
	cfg.headers["nethash"] = constants["nethash"]
	cfg.headers["version"] = constants["version"]
	cfg.fees = constants["fees"]

	select_peers()
	DAEMON_PEERS = rotate_peers()


def stop():
	global DAEMON_PEERS
	if DAEMON_PEERS != None:
		DAEMON_PEERS.set()
