# -*- coding: utf-8 -*-
# © Toons

import os
import pytz
from datetime import datetime

import dposlib
from dposlib import rest
from dposlib.ark import crypto
from dposlib.ark.v1 import api
from dposlib.ark.v1.mixin import loadPages
from dposlib.blockchain import cfg, Transaction
from dposlib.util.asynch import setInterval
from dposlib.util.data import loadJson, dumpJson


DAEMON_PEERS = None
TRANSACTIONS = {
	0: "send",
	1: "secondsignature",
	2: "delegate",
	3: "vote",
}
TYPING = {
	"timestamp": int,
	"type": int,
	"amount": int,
	"fee": int,
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
	version = rest.GET.api.peers.version().get('version', '0.0.0')
	height = rest.GET.api.blocks.getHeight().get('height', 0)
	if isinstance(height, dict) or isinstance(version, dict):
		return
		
	good_peers = list(sorted([
		peer for peer in rest.GET.api.peers().get('peers', []) if (
			peer.get("delay", 6000) <= cfg.timeout * 1000 and peer.get("version") == version and \
			peer.get("height", -1) > height - 10
		)
	], key=lambda e: e["delay"]))

	min_selection = getattr(cfg, "broadcast", 10)
	if len(good_peers) >= min_selection:
		cfg.peers = [
			"http://%(ip)s:%(port)s" % {"ip":peer["ip"], "port":rest.cfg.port} for \
			peer in good_peers[:min_selection]
		]


@setInterval(30)
def rotate_peers():
	select_peers()


def init():
	global DAEMON_PEERS
	cfg.begintime = datetime(*cfg.begintime, tzinfo=pytz.UTC)
	cfg.headers["API-Version"] = "1"
	
	if len(cfg.peers):
		network = rest.GET.api.loader.autoconfigure().get("network", {})
		cfg.hotmode = True if len(network) else False
		dumpJson(network, os.path.join(dposlib.ROOT, ".cold", cfg.network+".v1.cfg"))
	else:
		cfg.hotmode = False
		network = loadJson(os.path.join(dposlib.ROOT, ".cold", cfg.network+".v1.cfg"))

	if len(network):
		cfg.headers["version"] = str(network.pop('version'))
		cfg.headers["nethash"] = network.pop('nethash')
		cfg.__dict__.update(network)
		if len(cfg.peers):
			cfg.fees = rest.GET.api.blocks.getFees().get("fees", {})
			dumpJson(cfg.fees, os.path.join(dposlib.ROOT, ".cold", cfg.network+".v1.fee"))
		else:
			cfg.fees = loadJson(os.path.join(dposlib.ROOT, ".cold", cfg.network+".v1.fee"))

		# select peers immediately and keep refreshing them in a thread so we
		# are sure we make requests to working peers
		select_peers()
		DAEMON_PEERS = rotate_peers()
		Transaction.useStaticFee()
	else:
		raise Exception("Initialization error with peer %s" % response.get("peer", "???"))


def stop():
	global DAEMON_PEERS
	if DAEMON_PEERS != None:
		DAEMON_PEERS.set()


def computeDynamicFees(tx):
	raise NotImplementedError("No dynamic fees on ark v1 blockchain !")


def broadcastTransactions(*transactions, **params):
	chunk_size = params.pop("chunk_size", 20)
	report = []

	for chunk in [transactions[i:i+chunk_size] for i in range(0, len(transactions), chunk_size)]:
		response = rest.POST.peer.transactions(transactions=chunk)
		report.append(response)
	
	return None if len(report) == 0 else \
		   report[0] if len(report) == 1 else \
		   report


def transfer(amount, address, vendorField=None):
	return Transaction(
		type=0,
		amount=amount*100000000,
		recipientId=address,
		vendorField=vendorField
	)


def registerSecondSecret(secondSecret):
	return registerSecondPublicKey(crypto.getKeys(secondSecret)["publicKey"])

def registerSecondPublicKey(secondPublicKey):
	return Transaction(
		type=1,
		asset={
			"signature": {
				"publicKey": secondPublicKey
			}
		}
	)


def registerAsDelegate(username):
	return Transaction(
		type=2,
		asset={
			"delegate": {
				"username": username
			}
		}
	)


def upVote(*usernames):
	return Transaction(
		type=3,
		asset={
			"votes": {
				"username": ["+"+rest.GET.api.delegates.get(username=username, returnKey="delegate")["publicKey"] for username in usernames]
			}
		}
	)


def downVote(*usernames):
	return Transaction(
		type=3,
		asset={
			"votes": {
				"username": ["-"+rest.GET.api.delegates.get(username=username, returnKey="delegate")["publicKey"] for username in usernames]
			}
		}
	)

